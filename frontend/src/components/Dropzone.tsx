import { useCallback, useState } from 'react'
import type { DragEvent } from 'react'

export default function Dropzone({ onFile }: { onFile: (file: File) => void }){
  const [hover, setHover] = useState(false)

  const handleDrop = useCallback((e: DragEvent) => {
    e.preventDefault()
    setHover(false)
    const file = e.dataTransfer.files?.[0]
    if(file) onFile(file)
  }, [onFile])

  return (
    <label
      className={`block rounded-2xl border-2 border-dashed p-8 text-center cursor-pointer ${hover ? 'border-mint bg-white' : 'border-black/10 bg-white/70'}`}
      onDragOver={(e)=>{ e.preventDefault(); setHover(true) }}
      onDragLeave={()=> setHover(false)}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,.webp,.csv,.txt"
        onChange={(e)=>{ const file = e.target.files?.[0]; if(file) onFile(file) }}
        className="hidden"
      />
      <div className="text-lg font-display">Drop a document here</div>
      <p className="text-sm text-steel mt-2">PDF, image, CSV, or TXT</p>
    </label>
  )
}
