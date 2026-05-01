  /* ── Delete Vehicle ──────────────────────── */
  async function adminDeleteVehicle(vehicleId) {
    if (!confirm('Permanently delete this listing? This cannot be undone.')) return;
    try {
      const res = await fetch(`${API_BASE}/api/admin/vehicles/${vehicleId}`, {
        method: 'DELETE', headers: authHeaders()
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      document.getElementById(`vehicle-${vehicleId}`)?.remove();
      document.getElementById(`all-vehicle-${vehicleId}`)?.remove();
      await loadStats();
      alert('✅ Listing deleted.');
    } catch (err) {
      alert('Could not delete: ' + err.message);
    }
  }

  /* ── Delete User ──────────────────────────── */
  async function adminDeleteUser(userId, email) {
    if (!confirm(`Permanently delete user "${email}" and ALL their listings?\n\nThis CANNOT be undone.`)) return;
    try {
      const res = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
        method: 'DELETE',
        headers: authHeaders(),
      });
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        if (res.status === 404 || res.status === 405) throw new Error('ENDPOINT_MISSING');
        throw new Error(errBody.detail || `Server error ${res.status}`);
      }
      // Remove the user row from the table immediately
      document.querySelectorAll('#subscriptions-list tbody tr').forEach(row => {
        if (row.textContent.includes(email)) row.remove();
      });
      await loadStats();
      alert(`✅ User "${email}" has been deleted.`);
    } catch (err) {
      if (err.message === 'ENDPOINT_MISSING') {
        alert(
          '⚠️ The backend delete-user endpoint is not yet implemented on the server.\n\n' +
          'Ask your developer to add:\n  DELETE /api/admin/users/{user_id}\n\n' +
          'It should delete the user and cascade-delete all their listings.'
        );
      } else {
        alert('Could not delete user: ' + err.message);
      }
    }
  }
