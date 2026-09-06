import { FormEvent, useState } from "react";
import { ArrowRight, MessageCircle } from "lucide-react";

type Option = { label: string; value: string };
type Props = { question: string; options: Option[]; loading?: boolean; onAnswer: (answer: string) => void };

export function ClarificationCard({ question, options, loading, onAnswer }: Props) {
  const [customAnswer, setCustomAnswer] = useState("");
  const submit = (event: FormEvent) => { event.preventDefault(); if (customAnswer.trim()) onAnswer(customAnswer.trim()); };
  return <div className="clarification-card"><div className="clarification-label"><MessageCircle size={16} /> NEEDS YOUR INPUT</div><h3>{question}</h3><div className="clarification-options">{options.map((option) => <button key={option.value} disabled={loading} onClick={() => onAnswer(option.value)}>{option.label}<ArrowRight size={15} /></button>)}</div><form onSubmit={submit}><input value={customAnswer} onChange={(event) => setCustomAnswer(event.target.value)} placeholder="Or type your own answer..." disabled={loading} /><button aria-label="Submit answer" disabled={loading || !customAnswer.trim()}><ArrowRight size={16} /></button></form></div>;
}