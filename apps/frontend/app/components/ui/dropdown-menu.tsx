import * as React from "react"

const DropdownMenu = ({ children }: { children: React.ReactNode }) => {
  return <div className="relative inline-block">{children}</div>
}

const DropdownMenuTrigger = ({ children, onClick }: { children: React.ReactNode, onClick?: () => void }) => {
  return <div onClick={onClick}>{children}</div>
}

const DropdownMenuContent = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-50">
      {children}
    </div>
  )
}

const DropdownMenuItem = ({ children, onClick }: { children: React.ReactNode, onClick?: () => void }) => {
  return (
    <div 
      className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer"
      onClick={onClick}
    >
      {children}
    </div>
  )
}

export { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem }