export async function chatWithBackend(question) {
  const res = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
  if (!res.ok) throw new Error('Failed to get response from backend')
  return await res.json()
}

export async function uploadFileToBackend(formData) {
  const res = await fetch('http://localhost:8000/api/upload', {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) throw new Error('Failed to upload file')
  return await res.json()
}
