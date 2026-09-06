import { Database, MessageSquare } from "lucide-react";

type Props = { title: string; description: string; icon: "database" | "message" };

export function PlaceholderPage({ title, description, icon }: Props) {
  const Icon = icon === "database" ? Database : MessageSquare;
  return <div className="placeholder-page"><div className="placeholder-icon"><Icon size={24} /></div><div className="eyebrow">QUERYMIND</div><h1>{title}</h1><p>{description}</p></div>;
}
