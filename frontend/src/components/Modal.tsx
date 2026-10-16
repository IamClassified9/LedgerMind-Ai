import type { ReactNode } from "react";
import { X } from "lucide-react";

export default function Modal({title, onClose, children}: {title: string; onClose: () => void; children: ReactNode}) {
  return <div className="modal-backdrop" role="presentation" onMouseDown={e => {if (e.target === e.currentTarget) onClose();}}>
    <section className="modal" role="dialog" aria-modal="true" aria-label={title}>
      <header className="modal-head"><h2>{title}</h2><button className="icon-button" onClick={onClose} aria-label="Close"><X size={18}/></button></header>
      {children}
    </section>
  </div>;
}
