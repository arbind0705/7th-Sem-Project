import { useRef, useState } from 'react'

export function useVoiceRecorder() {
  const [recording, setRecording] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const mediaRecorder = useRef<MediaRecorder | null>(null)
  const chunks = useRef<Blob[]>([])

  async function start(withVideo: boolean) {
    setError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: withVideo })
      chunks.current = []
      const recorder = new MediaRecorder(stream)
      recorder.ondataavailable = (e) => chunks.current.push(e.data)
      recorder.start()
      mediaRecorder.current = recorder
      setRecording(true)
    } catch {
      setError('Microphone access was denied or is unavailable.')
    }
  }

  function stop(): Promise<Blob> {
    return new Promise((resolve) => {
      const recorder = mediaRecorder.current
      if (!recorder) return
      recorder.onstop = () => {
        recorder.stream.getTracks().forEach((t) => t.stop())
        setRecording(false)
        resolve(new Blob(chunks.current, { type: 'audio/webm' }))
      }
      recorder.stop()
    })
  }

  return { recording, error, start, stop }
}
