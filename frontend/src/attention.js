// What waits for the signed-in landlord: repair requests to approve. Shown as a badge in the menu
// and on the home page; read again when a decision is made.
import { reactive } from 'vue'
import { get } from './api'
import { space } from './session'

export const attention = reactive({ issues: [], loaded: false })

export async function loadAttention() {
  if (space() !== 'owner') return
  try {
    attention.issues = await get('list_issues')
  } catch {}
  attention.loaded = true
}

export const awaitingCount = () => attention.issues.filter((i) => i.approval === 'awaiting_approval').length
