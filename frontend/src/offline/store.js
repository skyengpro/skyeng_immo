// Small IndexedDB key-value store holding the last answer of every read, so the app still shows
// something useful with no connection. When IndexedDB is not available (a private window), an
// in-memory map keeps the app working for the visit.

const DB = 'sky_immo'
let dbPromise
const memory = new Map()

function open() {
  if (!dbPromise) {
    dbPromise = new Promise((resolve) => {
      try {
        const req = indexedDB.open(DB, 1)
        req.onupgradeneeded = () => req.result.createObjectStore('cache')
        req.onsuccess = () => resolve(req.result)
        req.onerror = req.onblocked = () => resolve(null)
      } catch {
        resolve(null)
      }
    })
  }
  return dbPromise
}

function run(mode, fn) {
  return open().then(
    (db) =>
      db &&
      new Promise((resolve) => {
        try {
          const tx = db.transaction('cache', mode)
          const req = fn(tx.objectStore('cache'))
          tx.oncomplete = () => resolve(req?.result)
          tx.onerror = tx.onabort = () => resolve(undefined)
        } catch {
          resolve(undefined)
        }
      }),
  )
}

export const cache = {
  async get(key) {
    const db = await open()
    return db ? run('readonly', (s) => s.get(key)) : memory.get(key)
  },
  async set(key, value) {
    const db = await open()
    if (!db) return memory.set(key, value)
    return run('readwrite', (s) => s.put(JSON.parse(JSON.stringify(value)), key))
  },
  async clear() {
    memory.clear()
    const db = await open()
    if (db) await run('readwrite', (s) => s.clear())
  },
}
