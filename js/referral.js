/* ============================================================
   pikCarz — Referral System (dashboard)
   ============================================================ */

const MILESTONES = [
  { target: 1,  reward: 'Priority Search Placement',  detail: '7 days — admin grants' },
  { target: 3,  reward: 'Founding Dealer Badge',       detail: 'Auto-awarded 🏅' },
  { target: 5,  reward: 'Featured Homepage Listing',   detail: '14 days — admin grants' },
  { target: 10, reward: 'PikCarz Ambassador Status',   detail: 'Auto-awarded 🌟' },
];

async function loadReferralStats() {
  try {
    const data = await api.getSilent('/api/referrals/my-stats');

    // Referral link
    const linkInput = document.getElementById('referral-link-input');
    if (linkInput) linkInput.value = data.referral_link;

    // Badges row
    const badgesDiv = document.getElementById('referral-badges');
    if (badgesDiv) {
      badgesDiv.innerHTML = [
        data.is_ambassador
          ? '<span style="background:linear-gradient(135deg,#f59e0b,#ef4444);color:#fff;padding:4px 12px;border-radius:100px;font-size:0.78rem;font-weight:700">🌟 Ambassador</span>'
          : '',
        data.is_founding_dealer
          ? '<span style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid #10b981;padding:4px 12px;border-radius:100px;font-size:0.78rem;font-weight:700">🏅 Founding Dealer</span>'
          : '',
        data.priority_search_active
          ? '<span style="background:rgba(59,130,246,0.15);color:#60a5fa;border:1px solid #3b82f6;padding:4px 12px;border-radius:100px;font-size:0.78rem;font-weight:700">⚡ Priority Search active</span>'
          : '',
      ].join('');
    }

    // Progress bar toward next milestone
    const progressDiv = document.getElementById('referral-progress');
    if (progressDiv) {
      if (data.next_milestone) {
        const count  = data.referral_count;
        const target = data.next_milestone.target;
        const pct    = Math.min(Math.round((count / target) * 100), 100);
        progressDiv.innerHTML = `
          <div style="display:flex;justify-content:space-between;font-size:0.83rem;margin-bottom:6px">
            <span style="color:var(--white)">${count} referral${count !== 1 ? 's' : ''} — next: <strong>${data.next_milestone.reward}</strong></span>
            <span style="color:var(--muted)">${count} / ${target}</span>
          </div>
          <div style="height:8px;background:var(--border);border-radius:4px">
            <div style="height:8px;background:linear-gradient(90deg,#ff4545,#ff8c42);border-radius:4px;width:${pct}%;transition:width 0.4s"></div>
          </div>`;
      } else {
        progressDiv.innerHTML = '<p style="color:#10b981;font-size:0.88rem;font-weight:600">🏆 All milestones reached! You\'re a PikCarz Ambassador.</p>';
      }
    }

    // Milestones table
    const tbody = document.getElementById('referral-milestones');
    if (tbody) {
      const count = data.referral_count;
      tbody.innerHTML = MILESTONES.map(m => {
        const done = count >= m.target;
        return `<tr style="border-bottom:1px solid var(--border)">
          <td style="padding:10px 12px;color:var(--white);font-weight:700">${m.target}</td>
          <td style="padding:10px 12px">
            <span style="color:var(--white)">${m.reward}</span>
            <span style="display:block;font-size:0.78rem;color:var(--muted)">${m.detail}</span>
          </td>
          <td style="padding:10px 12px">
            ${done
              ? '<span style="color:#10b981;font-weight:700">✓ Earned</span>'
              : `<span style="color:var(--muted);font-size:0.82rem">${m.target - count} more needed</span>`
            }
          </td>
        </tr>`;
      }).join('');
    }

  } catch (_) { /* non-critical — silently skip if not logged in */ }
}

function copyReferralLink() {
  const input = document.getElementById('referral-link-input');
  if (!input?.value) return;
  navigator.clipboard.writeText(input.value)
    .then(() => showToast('Referral link copied!', 'success'))
    .catch(() => {
      input.select();
      document.execCommand('copy');
      showToast('Link copied!', 'success');
    });
}

function shareReferralWhatsApp() {
  const link = document.getElementById('referral-link-input')?.value;
  if (!link) return;
  const msg = encodeURIComponent(
    `🚗 Hey! Join me on pikCarz — South Africa's fastest-growing vehicle marketplace.\n\nBuy, sell, and discover cars, bakkies, bikes & trucks.\n\nRegister here: ${link}`
  );
  window.open(`https://wa.me/?text=${msg}`, '_blank');
}

// Load on page ready
document.addEventListener('DOMContentLoaded', loadReferralStats);
