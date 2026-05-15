export default function ActionBar({
  saving,
  onSave,
  onValidate,
  onConfirm,
  onReject,
}: {
  saving: boolean
  onSave: () => void
  onValidate: () => void
  onConfirm: () => void
  onReject: () => void
}){
  return (
    <div className="flex flex-wrap gap-2 mt-6">
      <button onClick={onSave} className="px-4 py-2 rounded-full bg-ink text-white">
        {saving ? 'Saving...' : 'Save changes'}
      </button>
      <button onClick={onValidate} className="px-4 py-2 rounded-full bg-citrus text-ink">
        Validate
      </button>
      <button onClick={onConfirm} className="px-4 py-2 rounded-full bg-mint text-ink">
        Confirm
      </button>
      <button onClick={onReject} className="px-4 py-2 rounded-full bg-red-500 text-white">
        Reject
      </button>
    </div>
  )
}
