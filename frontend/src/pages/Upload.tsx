import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Dropzone from '../components/Dropzone'
import { getDocument, uploadDocument } from '../api/client'

export default function Upload(){
  const [progress, setProgress] = useState<number | null>(null)
  const [processing, setProcessing] = useState(false)
  const [processingStatus, setProcessingStatus] = useState<string | null>(null)
  const navigate = useNavigate()

  function sleep(ms: number){
    return new Promise((resolve) => setTimeout(resolve, ms))
  }

  async function waitForProcessing(id: string){
    setProcessing(true)
    setProcessingStatus('Processing document...')
    for(let i = 0; i < 30; i += 1){
      const res = await getDocument(id)
      const status = res.data?.status
      if(status){
        setProcessingStatus(`Status: ${status}`)
        if(status !== 'uploaded'){
          setProcessing(false)
          return
        }
      }
      await sleep(1000)
    }
    setProcessing(false)
  }

  async function handleFile(file: File){
    setProgress(0)
    try{
      const res = await uploadDocument(file, (p)=> setProgress(p))
      const id = res.data?.id
      if(id){
        await waitForProcessing(id)
        navigate('/')
      }
    }catch(err: any){
      setProgress(null)
      setProcessing(false)
      setProcessingStatus(null)
      alert(`Upload failed: ${err.message}`)
    }
  }

  return (
    <div className="max-w-2xl">
      <div className="text-xs uppercase tracking-widest text-steel">Upload</div>
      <h2 className="text-2xl font-display mb-4">Send a document for extraction</h2>
      <Dropzone onFile={handleFile} />
      {progress !== null && (
        <div className="mt-4">
          <div className="h-2 bg-black/10 rounded-full overflow-hidden">
            <div className="h-2 bg-mint" style={{ width: `${progress}%` }}></div>
          </div>
          <div className="text-xs text-steel mt-2">Uploading {progress}%</div>
        </div>
      )}
      {processing && (
        <div className="mt-4 rounded-xl border border-black/10 bg-white/70 p-3 text-sm">
          <div className="font-semibold">Processing</div>
          <div className="text-steel">{processingStatus || 'Working...'}</div>
        </div>
      )}
    </div>
  )
}
