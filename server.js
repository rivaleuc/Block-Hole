// BlockholeGen — Room WebSocket Server
// Run: node server.js
// Serves static files on :3000 + WebSocket on :3001

const http  = require('http')
const fs    = require('fs')
const path  = require('path')
const { WebSocketServer } = require('ws')

// ── Static file server ────────────────────────────────────────────────────────
const MIME = {
  '.html': 'text/html', '.js': 'application/javascript',
  '.css': 'text/css',   '.png': 'image/png',
  '.jpg': 'image/jpeg', '.svg': 'image/svg+xml',
  '.json': 'application/json', '.woff2': 'font/woff2',
}

const httpServer = http.createServer((req, res) => {
  let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : req.url)
  if (!fs.existsSync(filePath)) { res.writeHead(404); return res.end('Not found') }
  const ext  = path.extname(filePath)
  const mime = MIME[ext] || 'application/octet-stream'
  res.writeHead(200, { 'Content-Type': mime })
  fs.createReadStream(filePath).pipe(res)
})

httpServer.listen(3000, () => console.log('🎮 Game server: http://localhost:3000'))

// ── WebSocket room server ─────────────────────────────────────────────────────
const wss = new WebSocketServer({ port: 3001 })

const rooms = {}   // roomId → { players: [{ws, id, addr}], level, started, scores: [] }

function broadcast(room, msg) {
  const str = JSON.stringify(msg)
  room.players.forEach(p => {
    if (p.ws.readyState === 1) p.ws.send(str)
  })
}

function roomInfo(room) {
  return room.players.map(p => ({
    id:   p.id,
    addr: p.addr,
    done: p.done || false,
    moves: p.moves,
    time:  p.time,
    grade: p.grade,
    xp:    p.xp,
  }))
}

wss.on('connection', ws => {
  ws.on('message', raw => {
    let msg
    try { msg = JSON.parse(raw) } catch { return }

    // ── CREATE ROOM ──────────────────────────────────────────────────────────
    if (msg.type === 'create-room') {
      const { roomId, playerId, addr, level, isPublic } = msg
      if (rooms[roomId]) { ws.send(JSON.stringify({ type: 'error', message: 'Room already exists' })); return }
      rooms[roomId] = { players: [], level: level || 1, started: false, scores: [], isPublic: isPublic !== false }
      const player = { ws, id: playerId, addr: addr || playerId, done: false }
      rooms[roomId].players.push(player)
      ws._roomId   = roomId
      ws._playerId = playerId
      ws.send(JSON.stringify({ type: 'room-created', roomId, level: rooms[roomId].level, isPublic: rooms[roomId].isPublic }))
      console.log(`[Room] Created ${roomId} — host ${playerId} — ${rooms[roomId].isPublic ? 'public' : 'private'}`)
    }

    // ── JOIN ROOM ────────────────────────────────────────────────────────────
    else if (msg.type === 'join-room') {
      const { roomId, playerId, addr } = msg
      const room = rooms[roomId]
      if (!room) { ws.send(JSON.stringify({ type: 'error', message: 'Room not found. Check the code.' })); return }
      if (room.started) { ws.send(JSON.stringify({ type: 'error', message: 'Game already started' })); return }

      const player = { ws, id: playerId, addr: addr || playerId, done: false }
      room.players.push(player)
      ws._roomId   = roomId
      ws._playerId = playerId

      // Tell joiner the room info
      ws.send(JSON.stringify({ type: 'room-joined', roomId, level: room.level, players: roomInfo(room) }))

      // Tell everyone someone joined
      broadcast(room, { type: 'player-joined', playerId, addr: addr || playerId, count: room.players.length, players: roomInfo(room) })

      // Start game when 2+ players are in
      if (room.players.length >= 2 && !room.started) {
        room.started = true
        setTimeout(() => {
          broadcast(room, { type: 'game-start', level: room.level, players: roomInfo(room) })
          console.log(`[Room] Game started ${roomId} — ${room.players.length} players`)
        }, 1500)  // 1.5s delay so everyone sees "Opponent joined!"
      }
    }

    // ── SCORE SUBMITTED ──────────────────────────────────────────────────────
    else if (msg.type === 'score') {
      const room = rooms[ws._roomId]
      if (!room) return
      const player = room.players.find(p => p.id === ws._playerId)
      if (player) {
        player.done  = true
        player.moves = msg.moves
        player.time  = msg.time
        player.grade = msg.grade
        player.xp    = msg.xp
      }
      broadcast(room, { type: 'score', playerId: ws._playerId, addr: msg.addr, moves: msg.moves, time: msg.time, grade: msg.grade, xp: msg.xp, players: roomInfo(room) })

      // All done?
      if (room.players.every(p => p.done)) {
        broadcast(room, { type: 'room-complete', players: roomInfo(room) })
        console.log(`[Room] Complete ${ws._roomId}`)
      }
    }

    // ── GET ROOMS (lobby list) ────────────────────────────────────────────────
    else if (msg.type === 'get-rooms') {
      const available = Object.entries(rooms)
        .filter(([, r]) => !r.started && r.isPublic)
        .map(([id, r]) => ({
          roomId:  id,
          host:    r.players[0]?.addr || r.players[0]?.id || '???',
          level:   r.level,
          players: r.players.length,
        }))
      ws.send(JSON.stringify({ type: 'rooms-list', rooms: available }))
    }

    // ── PING ─────────────────────────────────────────────────────────────────
    else if (msg.type === 'ping') {
      ws.send(JSON.stringify({ type: 'pong' }))
    }
  })

  ws.on('close', () => {
    const room = rooms[ws._roomId]
    if (!room) return
    room.players = room.players.filter(p => p.ws !== ws)
    broadcast(room, { type: 'player-left', playerId: ws._playerId, count: room.players.length })
    if (room.players.length === 0) {
      delete rooms[ws._roomId]
      console.log(`[Room] Deleted ${ws._roomId}`)
    }
  })

  ws.on('error', () => {})
})

console.log('🔌 WebSocket server: ws://localhost:3001')
