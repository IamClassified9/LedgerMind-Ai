import "./export-polish.css";
import { Fragment, type ReactNode } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Activity, AlertCircle, ArrowDownRight, ArrowUpRight, BarChart3, BookOpen, Check, ChevronDown, Clock3, FilePlus2, KeyRound, LayoutDashboard, LoaderCircle, LogOut, Mail, Plus, RefreshCw, Search, ShieldCheck, Store, Truck, Utensils, UserRound, Wallet, X, FileSpreadsheet, FileText, Mic, MicOff, BrainCircuit, Save } from "lucide-react";
import { api, setAuthToken, type Business, type BusinessType, type RecordEntry, type RecordTemplate, type Report, type TemplateField, type IntelligenceIssue, type UserProfile, type SupplierInvoice, type BusinessAnalysis } from "./api/client";
import AuthScreen from "./components/AuthScreen";
import StatCard from "./components/StatCard";
import Modal from "./components/Modal";

const savedBusinessKey = "ledgermind.activeBusinessId";
const money = (value: number | undefined, currency = "NGN") => new Intl.NumberFormat("en-NG", {style:"currency", currency, maximumFractionDigits: 2}).format(value ?? 0);
const pretty = (value: string) => value.replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase());
const valueDate = (r: RecordEntry) => String(r.values.date || r.created_at || "");
const recordAmount = (r: RecordEntry) => Number(r.values.gross_amount ?? r.values.amount ?? r.values.paid_amount ?? r.values.refund_amount ?? 0) || 0;

type SpeechRecognitionLike = {
  lang: string; interimResults: boolean; maxAlternatives: number;
  onresult: ((event: {results: ArrayLike<{0: {transcript: string}; isFinal: boolean}>}) => void) | null;
  onerror: ((event: {error: string}) => void) | null; onend: (() => void) | null; start: () => void; stop: () => void;
};
type SpeechWindow = Window & {SpeechRecognition?: new () => SpeechRecognitionLike; webkitSpeechRecognition?: new () => SpeechRecognitionLike};

type DashboardProps = { user: UserProfile; onLogout: () => void; onUserUpdated: (user: UserProfile) => void };

const countryOptions = [
  {"code":"NG","name":"Nigeria","currency":"NGN","timezones":["Africa/Lagos"]},
  {"code":"GB","name":"United Kingdom","currency":"GBP","timezones":["Europe/London"]},
  {"code":"US","name":"United States","currency":"USD","timezones":["America/New_York","America/Chicago","America/Denver","America/Los_Angeles","America/Anchorage","Pacific/Honolulu"]},
  {"code":"JP","name":"Japan","currency":"JPY","timezones":["Asia/Tokyo"]},
  {"code":"CA","name":"Canada","currency":"CAD","timezones":["America/St_Johns","America/Halifax","America/Toronto","America/Winnipeg","America/Edmonton","America/Vancouver"]},
  {"code":"AU","name":"Australia","currency":"AUD","timezones":["Australia/Perth","Australia/Adelaide","Australia/Sydney","Australia/Brisbane","Australia/Darwin","Australia/Hobart"]},
  {"code":"GH","name":"Ghana","currency":"GHS","timezones":["Africa/Accra"]},
  {"code":"KE","name":"Kenya","currency":"KES","timezones":["Africa/Nairobi"]},
  {"code":"ZA","name":"South Africa","currency":"ZAR","timezones":["Africa/Johannesburg"]},
  {"code":"IN","name":"India","currency":"INR","timezones":["Asia/Kolkata"]},
  {"code":"DE","name":"Germany","currency":"EUR","timezones":["Europe/Berlin"]},
  {"code":"FR","name":"France","currency":"EUR","timezones":["Europe/Paris"]},
  {"code":"BR","name":"Brazil","currency":"BRL","timezones":["America/Sao_Paulo","America/Manaus","America/Rio_Branco"]},
  {"code":"MX","name":"Mexico","currency":"MXN","timezones":["America/Mexico_City","America/Cancun","America/Tijuana"]},
  {"code":"SG","name":"Singapore","currency":"SGD","timezones":["Asia/Singapore"]},
  {"code":"AE","name":"United Arab Emirates","currency":"AED","timezones":["Asia/Dubai"]},
  {"code":"CH","name":"Switzerland","currency":"CHF","timezones":["Europe/Zurich"]},
  {"code":"NZ","name":"New Zealand","currency":"NZD","timezones":["Pacific/Auckland"]},
  {"code":"CN","name":"China","currency":"CNY","timezones":["Asia/Shanghai"]},
  {"code":"KR","name":"South Korea","currency":"KRW","timezones":["Asia/Seoul"]},
  {"code":"PK","name":"Pakistan","currency":"PKR","timezones":["Asia/Karachi"]},
  {"code":"EG","name":"Egypt","currency":"EGP","timezones":["Africa/Cairo"]},
  {"code":"SA","name":"Saudi Arabia","currency":"SAR","timezones":["Asia/Riyadh"]},
  {"code":"IE","name":"Ireland","currency":"EUR","timezones":["Europe/Dublin"]},
  {"code":"ES","name":"Spain","currency":"EUR","timezones":["Europe/Madrid","Atlantic/Canary"]},
  {"code":"IT","name":"Italy","currency":"EUR","timezones":["Europe/Rome"]},
  {"code":"NL","name":"Netherlands","currency":"EUR","timezones":["Europe/Amsterdam"]},
  {"code":"SE","name":"Sweden","currency":"SEK","timezones":["Europe/Stockholm"]},
  {"code":"NO","name":"Norway","currency":"NOK","timezones":["Europe/Oslo"]},
  {"code":"DK","name":"Denmark","currency":"DKK","timezones":["Europe/Copenhagen"]},
  {"code":"ID","name":"Indonesia","currency":"IDR","timezones":["Asia/Jakarta","Asia/Makassar","Asia/Jayapura"]},
  {"code":"PH","name":"Philippines","currency":"PHP","timezones":["Asia/Manila"]},
  {"code":"TH","name":"Thailand","currency":"THB","timezones":["Asia/Bangkok"]},
  {"code":"TR","name":"Türkiye","currency":"TRY","timezones":["Europe/Istanbul"]},
  {"code":"UA","name":"Ukraine","currency":"UAH","timezones":["Europe/Kyiv"]},
  {"code":"AR","name":"Argentina","currency":"ARS","timezones":["America/Argentina/Buenos_Aires"]},
  {"code":"CL","name":"Chile","currency":"CLP","timezones":["America/Santiago","Pacific/Easter"]},
  {"code":"CO","name":"Colombia","currency":"COP","timezones":["America/Bogota"]},
  {"code":"PE","name":"Peru","currency":"PEN","timezones":["America/Lima"]},
  {"code":"IL","name":"Israel","currency":"ILS","timezones":["Asia/Jerusalem"]},
  {"code":"QA","name":"Qatar","currency":"QAR","timezones":["Asia/Qatar"]},
  {"code":"MA","name":"Morocco","currency":"MAD","timezones":["Africa/Casablanca"]},
  {"code":"ET","name":"Ethiopia","currency":"ETB","timezones":["Africa/Addis_Ababa"]},
  {"code":"UG","name":"Uganda","currency":"UGX","timezones":["Africa/Kampala"]},
  {"code":"TZ","name":"Tanzania","currency":"TZS","timezones":["Africa/Dar_es_Salaam"]},
  {"code":"ZM","name":"Zambia","currency":"ZMW","timezones":["Africa/Lusaka"]},
  {"code":"RW","name":"Rwanda","currency":"RWF","timezones":["Africa/Kigali"]},
];

function renderMarkdown(markdown: string): ReactNode {
  const renderInline = (line: string): React.ReactNode[] => {
    const parts = line.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);
    return parts.map((part, index) => {
      if (part.startsWith("**") && part.endsWith("**")) return <strong key={index}>{part.slice(2, -2)}</strong>;
      if (part.startsWith("*") && part.endsWith("*") && part.length > 2) return <em key={index}>{part.slice(1, -1)}</em>;
      if (part.startsWith("`") && part.endsWith("`")) return <code key={index}>{part.slice(1, -1)}</code>;
      return <Fragment key={index}>{part}</Fragment>;
    });
  };
  const lines = markdown.replace(/\r/g, "").split("\n");
  const blocks: React.ReactNode[] = [];
  let list: string[] = [];
  let orderedList = false;
  const flushList = () => {
    if (list.length) {
      const ListTag = orderedList ? "ol" : "ul";
      blocks.push(<ListTag key={`list-${blocks.length}`}>{list.map((item, i) => <li key={i}>{renderInline(item)}</li>)}</ListTag>);
      list = []; orderedList = false;
    }
  };
  lines.forEach((raw, index) => {
    const line = raw.trim();
    if (!line) { flushList(); return; }
    const heading = /^(#{1,3})\s+(.+)$/.exec(line);
    const bullet = /^(?:[-*•])\s+(.+)$/.exec(line);
    const numbered = /^\d+[.)]\s+(.+)$/.exec(line);
    if (/^(---+|___+|\*\*\*+)$/.test(line)) { flushList(); blocks.push(<hr key={index}/>); return; }
    if (bullet) { if (list.length && orderedList) flushList(); orderedList = false; list.push(bullet[1]); return; }
    if (numbered) { if (list.length && !orderedList) flushList(); orderedList = true; list.push(numbered[1]); return; }
    flushList();
    if (heading) {
      const content = renderInline(heading[2]);
      if (heading[1].length === 1) blocks.push(<h3 key={index}>{content}</h3>);
      else if (heading[1].length === 2) blocks.push(<h4 key={index}>{content}</h4>);
      else blocks.push(<h5 key={index}>{content}</h5>);
    } else {
      blocks.push(<p key={index}>{renderInline(line)}</p>);
    }
  });
  flushList();
  return <div className="markdown-content">{blocks}</div>;
}

function markdownToHtml(markdown: string, escapeHtml: (value: unknown) => string): string {
  const lines = String(markdown || "").replace(/\r/g, "").split("\n");
  const inline = (value: string) => escapeHtml(value)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*]+)\*(?!\*)/g, "$1<em>$2</em>");
  const out: string[] = [];
  let list: string[] = [];
  let ordered = false;
  const flush = () => {
    if (!list.length) return;
    const tag = ordered ? "ol" : "ul";
    out.push(`<${tag}>${list.map(item => `<li>${inline(item)}</li>`).join("")}</${tag}>`);
    list = []; ordered = false;
  };
  for (const raw of lines) {
    const line = raw.trim();
    if (!line) { flush(); continue; }
    if (/^(---+|___+|\*\*\*+)$/.test(line)) { flush(); out.push("<hr>"); continue; }
    const heading = /^(#{1,3})\s+(.+)$/.exec(line);
    if (heading) { flush(); const tag = `h${heading[1].length + 1}`; out.push(`<${tag}>${inline(heading[2])}</${tag}>`); continue; }
    const bullet = /^(?:[-*•])\s+(.+)$/.exec(line);
    const number = /^\d+[.)]\s+(.+)$/.exec(line);
    if (bullet || number) {
      const nextOrdered = Boolean(number);
      if (list.length && ordered !== nextOrdered) flush();
      ordered = nextOrdered; list.push((bullet || number)![1]); continue;
    }
    flush(); out.push(`<p>${inline(line)}</p>`);
  }
  flush();
  return out.join("\n");
}

function Dashboard({ user, onLogout, onUserUpdated }: DashboardProps) {
  const [business, setBusiness] = useState<Business | null>(null);
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [templates, setTemplates] = useState<RecordTemplate[]>([]);
  const [records, setRecords] = useState<RecordEntry[]>([]);
  const [supplierInvoices, setSupplierInvoices] = useState<SupplierInvoice[]>([]);
  const [report, setReport] = useState<Report | null>(null);
  const [period, setPeriod] = useState("monthly");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [apiOnline, setApiOnline] = useState(false);
  const [activeNav, setActiveNav] = useState("Overview");
  const [query, setQuery] = useState("");
  const [showBusinessModal, setShowBusinessModal] = useState(false);
  const [showRecordModal, setShowRecordModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [profileName, setProfileName] = useState(user.full_name);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [profileSaving, setProfileSaving] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const [notice, setNotice] = useState("");
  const [businessName, setBusinessName] = useState("");
  const [businessCountry, setBusinessCountry] = useState("NG");
  const [businessTimezone, setBusinessTimezone] = useState("Africa/Lagos");
  const [businessType, setBusinessType] = useState<BusinessType>("restaurant");
  const [farmModules, setFarmModules] = useState<Array<"crops" | "livestock" | "poultry">>(["crops"]);
  const [saving, setSaving] = useState(false);
  const [recordValues, setRecordValues] = useState<Record<string, string>>({});
  const [aiNote, setAiNote] = useState("");
  const [aiResult, setAiResult] = useState<Record<string, unknown> | null>(null);
  const [aiBusy, setAiBusy] = useState(false);
  const [aiError, setAiError] = useState("");
  const [invoiceSaving, setInvoiceSaving] = useState(false);
  const [voiceListening, setVoiceListening] = useState(false);
  const [analystQuestion, setAnalystQuestion] = useState("");
  const [analystResult, setAnalystResult] = useState<BusinessAnalysis | null>(null);
  const [analystBusy, setAnalystBusy] = useState(false);
  const [analystError, setAnalystError] = useState("");
  const [overviewQuestion, setOverviewQuestion] = useState("");
  const [overviewAnswer, setOverviewAnswer] = useState<BusinessAnalysis | null>(null);
  const [overviewBusy, setOverviewBusy] = useState(false);
  const [overviewError, setOverviewError] = useState("");
  const [overviewVoiceListening, setOverviewVoiceListening] = useState(false);
  const [intelligenceIssues, setIntelligenceIssues] = useState<IntelligenceIssue[]>([]);
  const [intelligenceNotice, setIntelligenceNotice] = useState("");

  const load = useCallback(async (id?: string, selectedPeriod = period) => {
    setError("");
    setRefreshing(true);
    try {
      await api.live();
      setApiOnline(true);
      const availableBusinesses = await api.businesses();
      setBusinesses(availableBusinesses);
      let currentId = id || business?.id || localStorage.getItem(savedBusinessKey) || "";
      if (!availableBusinesses.some(item => item.id === currentId)) currentId = availableBusinesses[0]?.id || "";
      if (!currentId) {
        localStorage.removeItem(savedBusinessKey);
        setBusiness(null); setTemplates([]); setRecords([]); setSupplierInvoices([]); setReport(null); setIntelligenceIssues([]); setIntelligenceNotice("");
        return;
      }
      if (business?.id && business.id !== currentId) {
        // Never carry a preview or answer from one workspace into another.
        setAiNote(""); setAiResult(null); setAiError("");
        setAnalystResult(null); setAnalystError("");
      }
      const current = await api.business(currentId);
      const [templateList, recordList, reportData, invoiceList] = await Promise.all([
        api.templates(currentId), api.records(currentId), api.report(currentId, selectedPeriod), api.supplierInvoices(currentId),
      ]);
      setBusiness(current);
      setTemplates(templateList);
      setRecords(recordList);
      setSupplierInvoices(invoiceList);
      setReport(reportData);
      // Intelligence is additive: an issue endpoint failure must not break the main dashboard.
      try {
        const intelligence = await api.intelligenceIssues(currentId);
        setIntelligenceIssues(intelligence.issues || []);
        setIntelligenceNotice(intelligence.notice || "");
      } catch {
        setIntelligenceIssues([]);
        setIntelligenceNotice("Issue detection is temporarily unavailable. Your records and reports are unaffected.");
      }
      setSelectedTemplate(prev => templateList.some(t => t.id === prev) ? prev : (templateList[0]?.id || ""));
      localStorage.setItem(savedBusinessKey, current.id);
    } catch (e) {
      setApiOnline(false);
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setRefreshing(false);
      setLoading(false);
    }
  }, [business?.id, period]);

  useEffect(() => {
    const id = localStorage.getItem(savedBusinessKey) || "";
    void load(id);
    // load is intentionally called once on startup; user actions invoke it explicitly.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (business?.id) void load(business.id, period);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [period]);

  const filteredRecords = useMemo(() => records.filter(r => {
    const template = templates.find(t => t.id === r.template_id);
    const searchable = `${template?.name || ""} ${JSON.stringify(r.values)}`.toLowerCase();
    return searchable.includes(query.toLowerCase());
  }), [records, templates, query]);

  const totalRecords = report?.data_quality.records_in_period ?? 0;
  const sales = report?.totals.sales_revenue ?? 0;
  const expenses = report?.totals.operating_expenses ?? 0;
  const purchases = report?.totals.purchases ?? 0;
  const salesChange = report?.comparison_to_previous_period.sales_revenue_change_percent;
  const reconciliationDifference = report?.reconciliation.sales_minus_incoming_payments ?? 0;

  async function createBusiness(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setError("");
    try {
      const created = await api.createBusiness({name:businessName.trim(), business_type:businessType, country:businessCountry, currency:countryOptions.find(item => item.code === businessCountry)?.currency || "NGN", timezone:businessTimezone, ...(businessType === "farm" ? {farm_modules:farmModules} : {})});
      setBusinessName(""); setShowBusinessModal(false); setNotice(`Created ${created.name}. Starter record templates are ready.`);
      await load(created.id);
    } catch (e) { setError(e instanceof Error ? e.message : "Could not create business."); }
    finally { setSaving(false); }
  }

  function downloadFile(filename: string, content: string, mimeType: string) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function exportAiAnalysisCsv() {
    if (!business || !aiResult) return;
    const outstanding = aiResult.invoice_amount == null || aiResult.amount_paid == null
      ? "" : Math.max(0, Number(aiResult.invoice_amount) - Number(aiResult.amount_paid));
    const rows: Array<[string, unknown]> = [
      ["Business", business.name],
      ["Analysis status", "AI-generated — pending human review"],
      ["Transaction type", aiResult.transaction_type],
      ["Party / supplier", aiResult.party_name],
      ["Direction", aiResult.direction],
      ["Invoice amount", aiResult.invoice_amount],
      ["Amount paid", aiResult.amount_paid],
      ["Outstanding balance (calculated)", outstanding],
      ["Currency", aiResult.currency],
      ["Transaction date", aiResult.transaction_date],
      ["Reference", aiResult.reference],
      ["Note", aiResult.note],
      ["Missing information", Array.isArray(aiResult.missing_information) ? aiResult.missing_information.join("; ") : ""],
      ["Ambiguities", Array.isArray(aiResult.ambiguity) ? aiResult.ambiguity.join("; ") : ""],
      ["Original input", aiNote],
    ];
    const csvCell = (value: unknown) => `"${String(value ?? "").replaceAll('"', '""')}"`;
    const csv = ["Field,Value", ...rows.map(([key, value]) => `${csvCell(key)},${csvCell(value)}`)].join("\r\n");
    downloadFile(`${business.name.replace(/[^a-z0-9-_]+/gi, "-")}-ai-analysis-${new Date().toISOString().slice(0,10)}.csv`, "\uFEFF" + csv, "text/csv;charset=utf-8");
    setNotice("Downloaded the AI analysis. It is a review preview, not a saved business record.");
  }

  function exportAiAnalysisDocument() {
    if (!business || !aiResult) return;
    const outstanding = aiResult.invoice_amount == null || aiResult.amount_paid == null
      ? "Needs review" : money(Math.max(0, Number(aiResult.invoice_amount) - Number(aiResult.amount_paid)), business.currency);
    const field = (label: string, value: unknown) => `<div class="field"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value == null || value === "" ? "Not provided" : value)}</strong></div>`;
    const list = (value: unknown) => Array.isArray(value) && value.length ? `<ul>${value.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : "<p>None identified.</p>";
    const html = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Analysis — ${escapeHtml(aiResult.party_name || "Business record")}</title><style>
      *{box-sizing:border-box}body{font:14px/1.55 Arial,Helvetica,sans-serif;color:#1b2b21;margin:0;background:#f2f5f2}.page{max-width:900px;margin:32px auto;background:#fff;padding:42px;border:1px solid #dce5de}header{border-bottom:3px solid #6aab43;padding-bottom:20px} .brand{font-size:12px;letter-spacing:2px;color:#4c7b38;font-weight:700}h1{font-size:30px;margin:10px 0 4px}h2{font-size:16px;margin:28px 0 12px}p{margin:8px 0;color:#536358}.status{display:inline-block;background:#fff0d8;color:#85520a;border-radius:20px;padding:5px 10px;font-size:11px;font-weight:700}.summary{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:22px 0}.metric{padding:16px;background:#f3f7f3;border:1px solid #dce7dc;border-radius:8px}.metric span,.field span{display:block;color:#5c6d61;font-size:12px;margin-bottom:5px}.metric strong{font-size:21px}.fields{display:grid;grid-template-columns:repeat(2,1fr);gap:0 22px}.field{padding:12px 0;border-bottom:1px solid #e4ebe5;overflow-wrap:anywhere}.field strong{font-weight:600}.callout{padding:14px;border-radius:7px;background:#fff6e5;border:1px solid #efdfba;color:#694b18}footer{border-top:1px solid #dce5de;margin-top:30px;padding-top:14px;font-size:11px;color:#637267}@media(max-width:650px){.page{margin:0;padding:22px}.summary{grid-template-columns:1fr}.fields{grid-template-columns:1fr}}@media print{body{background:#fff}.page{margin:0;border:0;max-width:none;padding:10mm}}
      </style></head><body><main class="page"><header><div class="brand">${escapeHtml(business.name.toUpperCase())} · LEDGERMIND AI</div><h1>AI Record Analysis</h1><p>${escapeHtml(pretty(String(aiResult.transaction_type || "unknown")))} · Generated ${escapeHtml(new Date().toLocaleString())}</p><span class="status">AI-GENERATED · HUMAN REVIEW REQUIRED</span></header><section class="summary"><div class="metric"><span>Invoice amount</span><strong>${escapeHtml(aiResult.invoice_amount == null ? "Not provided" : money(Number(aiResult.invoice_amount), business.currency))}</strong></div><div class="metric"><span>Amount paid</span><strong>${escapeHtml(aiResult.amount_paid == null ? "Not provided" : money(Number(aiResult.amount_paid), business.currency))}</strong></div><div class="metric"><span>Outstanding · calculated</span><strong>${escapeHtml(outstanding)}</strong></div></section><h2>Extracted details</h2><div class="fields">${field("Supplier / party", aiResult.party_name)}${field("Who owes whom", pretty(String(aiResult.direction || "unknown")))}${field("Transaction date", aiResult.transaction_date)}${field("Reference", aiResult.reference)}${field("Currency", aiResult.currency)}${field("Transaction type", pretty(String(aiResult.transaction_type || "unknown")))}</div><h2>Note</h2><p>${escapeHtml(aiResult.note || "No note returned.")}</p><h2>Original text submitted</h2><p>${escapeHtml(aiNote)}</p><h2>Missing information</h2>${list(aiResult.missing_information)}<h2>Ambiguities to review</h2>${list(aiResult.ambiguity)}<div class="callout"><strong>Important:</strong> This document records an AI-generated interpretation only. It is not a saved business record, proof of payment, or accounting advice. Verify every field against the source document before taking action. The outstanding balance is calculated from the extracted amounts.</div><footer>Generated by LedgerMind AI · ${escapeHtml(business.name)} · This analysis has not been saved as a business record.</footer></main></body></html>`;
    downloadFile(`${business.name.replace(/[^a-z0-9-_]+/gi, "-")}-ai-analysis-${new Date().toISOString().slice(0,10)}.html`, html, "text/html;charset=utf-8");
    setNotice("Downloaded a formatted AI analysis document. It remains a review preview, not a saved record.");
  }

  function exportRecordsCsv() {
    if (!business) return;
    const rows: Array<Record<string, unknown>> = filteredRecords.map(record => {
      const template = templates.find(item => item.id === record.template_id);
      return {
        business: business.name,
        record_type: template?.name || "Business record",
        date: valueDate(record).slice(0, 10),
        amount: recordAmount(record),
        record_id: record.id,
        ...record.values,
      };
    });
    const matchingInvoices = supplierInvoices.filter(invoice =>
      `${invoice.supplier} ${invoice.reference || ""} ${invoice.note || ""}`.toLowerCase().includes(query.toLowerCase())
    );
    rows.push(...matchingInvoices.map(invoice => ({
      business: business.name,
      record_type: "Supplier Invoice",
      date: invoice.transaction_date,
      amount: Number(invoice.invoice_amount),
      record_id: invoice.id,
      supplier: invoice.supplier,
      invoice_amount: Number(invoice.invoice_amount),
      amount_paid: Number(invoice.amount_paid),
      outstanding_amount: Number(invoice.outstanding_amount),
      currency: invoice.currency,
      reference: invoice.reference || "",
      direction: invoice.direction,
      note: invoice.note || "",
      source_note: invoice.source_note || "",
    })));
    const columns = Array.from(new Set(["business", "record_type", "date", "amount", "record_id", ...rows.flatMap(row => Object.keys(row))]));
    const escapeCsv = (value: unknown) => `"${String(value ?? "").replaceAll('"', '""')}"`;
    const csv = [columns.map(escapeCsv).join(","), ...rows.map(row => columns.map(column => escapeCsv(row[column])).join(","))].join("\r\n");
    downloadFile(`${business.name.replace(/[^a-z0-9-_]+/gi, "-")}-records-${new Date().toISOString().slice(0,10)}.csv`, "\uFEFF" + csv, "text/csv;charset=utf-8");
    setNotice(`Exported ${rows.length} saved record${rows.length === 1 ? "" : "s"} (including confirmed supplier invoices where present) as a spreadsheet-compatible CSV.`);
  }

  function exportRecordsDocument() {
    if (!business) return;
    const recordRows = filteredRecords.map(record => {
      const template = templates.find(item => item.id === record.template_id);
      const details = Object.entries(record.values).map(([key, value]) => `<div class="detail"><span>${escapeHtml(pretty(key))}</span><strong>${escapeHtml(value)}</strong></div>`).join("");
      return `<tr><td>${escapeHtml(template?.name || "Business record")}</td><td>${escapeHtml(valueDate(record).slice(0,10))}</td><td>${escapeHtml(money(recordAmount(record), business.currency))}</td><td>${details || "—"}</td></tr>`;
    });
    const invoiceRows = supplierInvoices.filter(invoice =>
      `${invoice.supplier} ${invoice.reference || ""} ${invoice.note || ""}`.toLowerCase().includes(query.toLowerCase())
    ).map(invoice => `<tr><td>Supplier Invoice</td><td>${escapeHtml(invoice.transaction_date)}</td><td>${escapeHtml(money(Number(invoice.invoice_amount), business.currency))}</td><td><div class="detail"><span>Supplier</span><strong>${escapeHtml(invoice.supplier)}</strong></div><div class="detail"><span>Reference</span><strong>${escapeHtml(invoice.reference || "Not provided")}</strong></div><div class="detail"><span>Amount paid</span><strong>${escapeHtml(money(Number(invoice.amount_paid), business.currency))}</strong></div><div class="detail"><span>Outstanding</span><strong>${escapeHtml(money(Number(invoice.outstanding_amount), business.currency))}</strong></div><div class="detail"><span>Note</span><strong>${escapeHtml(invoice.note || "")}</strong></div></td></tr>`);
    const rows = [...recordRows, ...invoiceRows].join("");
    const exportedCount = recordRows.length + invoiceRows.length;
    const html = `<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(business.name)} records</title><style>body{font:14px Arial,sans-serif;color:#17251c;margin:36px}h1{margin-bottom:4px}p{color:#526257}.meta{margin:20px 0}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccd5ce;padding:10px;text-align:left;vertical-align:top;white-space:normal}th{background:#edf3ee}td:last-child{max-width:460px;overflow-wrap:anywhere}.detail{margin:0 0 8px}.detail span{display:block;color:#617067;font-size:11px}.detail strong{font-weight:500}footer{margin-top:28px;color:#617067;font-size:12px}@media print{body{margin:12mm}}</style></head><body><h1>${escapeHtml(business.name)}</h1><p>Business records export</p><div class="meta">Business type: ${escapeHtml(pretty(business.business_type))} · Exported: ${new Date().toLocaleString()} · Records: ${exportedCount}</div><table><thead><tr><th>Record type</th><th>Date</th><th>Amount</th><th>Record details</th></tr></thead><tbody>${rows || '<tr><td colspan="4">No saved records in this selection.</td></tr>'}</tbody></table><footer>Exported from LedgerMind AI. This document reflects saved records only; verify against source documents.</footer></body></html>`;
    downloadFile(`${business.name.replace(/[^a-z0-9-_]+/gi, "-")}-records-${new Date().toISOString().slice(0,10)}.html`, html, "text/html;charset=utf-8");
    setNotice(`Downloaded a document containing ${exportedCount} saved record${exportedCount === 1 ? "" : "s"}, including confirmed supplier invoices where present. Open it in a browser or Microsoft Word to print or save as PDF.`);
  }

  function escapeHtml(value: unknown): string {
    return String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;", "'":"&#39;"}[char] || char));
  }

  async function interpretNote(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setAiBusy(true); setAiError(""); setAiResult(null);
    try { const response = await api.interpretNote(aiNote, business?.id); setAiResult(response.extraction); setNotice("AI extraction completed. Review the fields before using them."); }
    catch (e) { setAiError(e instanceof Error ? e.message : "AI extraction failed."); }
    finally { setAiBusy(false); }
  }

  function updateAiField(key: string, value: unknown) {
    setAiResult(previous => previous ? {...previous, [key]: value} : previous);
  }

  function startVoiceInput() {
    const speech = window as SpeechWindow;
    const Recognition = speech.SpeechRecognition || speech.webkitSpeechRecognition;
    if (!Recognition) {
      setAiError("Voice input is not supported by this browser. Use the text field or try a supported Chromium browser.");
      return;
    }
    const recognition = new Recognition();
    recognition.lang = "en-NG";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = event => {
      const transcript = Array.from(event.results).filter(result => result.isFinal).map(result => result[0].transcript).join(" ").trim();
      if (transcript) setAiNote(previous => previous.trim() ? `${previous.trim()} ${transcript}` : transcript);
    };
    recognition.onerror = event => setAiError(`Voice input failed (${event.error}). You can type the note instead.`);
    recognition.onend = () => setVoiceListening(false);
    setAiError("");
    setVoiceListening(true);
    try { recognition.start(); } catch { setVoiceListening(false); setAiError("Could not start voice input. Check microphone permission and try again."); }
  }

  function startOverviewVoiceInput() {
    const speech = window as SpeechWindow;
    const Recognition = speech.SpeechRecognition || speech.webkitSpeechRecognition;
    if (!Recognition) {
      setOverviewError("Voice input is not supported by this browser. Type your question or try a supported Chromium browser.");
      return;
    }
    const recognition = new Recognition();
    recognition.lang = "en-NG";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = event => {
      const transcript = Array.from(event.results).filter(result => result.isFinal).map(result => result[0].transcript).join(" ").trim();
      if (transcript) setOverviewQuestion(previous => previous.trim() ? `${previous.trim()} ${transcript}` : transcript);
    };
    recognition.onerror = event => setOverviewError(`Voice input failed (${event.error}). You can type your question instead.`);
    recognition.onend = () => setOverviewVoiceListening(false);
    setOverviewError("");
    setOverviewVoiceListening(true);
    try { recognition.start(); } catch { setOverviewVoiceListening(false); setOverviewError("Could not start voice input. Check microphone permission and try again."); }
  }

  function continueAsBusinessRecord() {
    if (!business || !aiResult) return;
    const note = aiNote.toLowerCase();
    const recordType = String(aiResult.record_type || "unclear").toLowerCase();
    if (recordType === "none") {
      setAiError("This note does not describe a business transaction. Nothing has been saved. Enter a sale, expense, supplier invoice, or supplier payment.");
      return;
    }
    if (recordType === "unclear") {
      setAiError("I couldn't confidently classify this note. Please clarify whether it is a sale, expense, supplier invoice, or supplier payment. Nothing has been saved.");
      return;
    }
    if (recordType === "supplier_invoice") {
      if (String(aiResult.direction || "unknown") !== "business_owes_party") {
        setAiError("This appears to be a supplier invoice, but who owes whom is unclear. Review the direction and confirm it before saving. Nothing has been saved.");
        return;
      }
      setAiError("This note is classified as a supplier invoice. Review the extracted fields and use Confirm and save invoice. Nothing has been saved yet.");
      return;
    }
    const isSale = recordType === "sale";
    const isExpense = recordType === "expense" || recordType === "supplier_payment";
    let target: RecordTemplate | undefined;

    if (isSale) {
      target = templates.find(template => {
        const keys = template.fields.map(field => String(field.key || field.name || "").toLowerCase());
        return keys.includes("gross_amount") && keys.includes("payment_method");
      }) || templates.find(template => /sales|sale|dispensing/i.test(`${template.key} ${template.name}`));
    } else if (isExpense) {
      target = templates.find(template => /expense|purchase|cost|payment/i.test(`${template.key} ${template.name}`));
    }

    if (!target) {
      setAiError(`The AI classified this note as ${recordType.replaceAll("_", " ")}, but this business has no matching template. Use Add record to choose a template; nothing has been saved.`);
      return;
    }

    const today = new Date().toISOString().slice(0, 10);
    const sourceAmount = recordType === "sale" ? (aiResult.amount_paid ?? aiResult.invoice_amount) : (aiResult.amount_paid ?? aiResult.invoice_amount);
    const amount = sourceAmount == null ? "" : String(sourceAmount);
    const values: Record<string, string> = {};
    for (const field of target.fields) {
      const key = String(field.key || field.name || "");
      const lower = key.toLowerCase();
      if (lower === "date" || lower.endsWith("_date")) values[key] = String(aiResult.transaction_date || today);
      else if (["gross_amount", "sales_amount", "amount", "total_amount", "cost", "expense_amount", "paid_amount"].includes(lower) && amount) values[key] = amount;
      else if (lower === "payment_method") {
        values[key] = /\bcash\b/.test(note) ? "cash" : /\btransfer\b/.test(note) ? "transfer" : /\bcard\b/.test(note) ? "card" : "other";
      } else if (["notes", "note", "description", "details", "item", "product_name"].includes(lower)) values[key] = aiNote;
    }
    setSelectedTemplate(target.id);
    setRecordValues(values);
    setShowRecordModal(true);
    setAiError("");
  }

  async function routeTransactionNote(note: string, source: "overview" | "reports"): Promise<boolean> {
    if (!business || !note.trim()) return false;
    const interpreted = await api.interpretNote(note.trim(), business?.id);
    const extraction = interpreted.extraction;
    const type = String(extraction.record_type || "unclear").toLowerCase();
    if (["sale", "expense", "supplier_invoice", "supplier_payment"].includes(type)) {
      setAiNote(note.trim());
      setAiResult(extraction);
      setAiError("");
      setActiveNav("Records");
      setNotice(`AI classified this note as ${type.replaceAll("_", " ")}. Review the extracted fields before saving.`);
      return true;
    }
    if (type === "unclear") {
      const message = "I couldn't confidently classify this as a transaction. Clarify whether it is a sale, expense, supplier invoice, or supplier payment, or ask a general business question instead. Nothing has been saved.";
      if (source === "overview") setOverviewError(message); else setAnalystError(message);
      return true;
    }
    return false;
  }

  async function saveReviewedInvoice() {
    if (!business || !aiResult) return;
    const supplier = String(aiResult.party_name || "").trim();
    if (String(aiResult.direction || "unknown") !== "business_owes_party") {
      setAiError("This supplier-invoice workflow is for invoices the business owes to a supplier. Confirm the direction before saving.");
      return;
    }
    const invoiceAmount = Number(aiResult.invoice_amount);
    const amountPaid = Number(aiResult.amount_paid);
    const transactionDate = String(aiResult.transaction_date || "");
    if (!supplier || aiResult.invoice_amount == null || !Number.isFinite(invoiceAmount) || invoiceAmount < 0 || aiResult.amount_paid == null || !Number.isFinite(amountPaid) || amountPaid < 0 || !/^\d{4}-\d{2}-\d{2}$/.test(transactionDate)) {
      setAiError("Before saving, provide a supplier, valid invoice amount, amount paid (enter 0 if none), and transaction date.");
      return;
    }
    setInvoiceSaving(true); setAiError("");
    try {
      await api.createSupplierInvoice(business.id, {
        supplier, invoice_amount: invoiceAmount, amount_paid: amountPaid, transaction_date: transactionDate,
        reference: String(aiResult.reference || "").trim() || null,
        direction: String(aiResult.direction || "business_owes_party"),
        note: String(aiResult.note || "").trim() || null, source_note: aiNote,
      });
      setAiResult(null);
      setNotice("Reviewed supplier invoice saved. It is now available in Records and report summaries.");
      await load(business.id, period);
      setActiveNav("Records");
    } catch (e) { setAiError(e instanceof Error ? e.message : "Could not save supplier invoice."); }
    finally { setInvoiceSaving(false); }
  }

  async function runBusinessAnalysis(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!business) return;
    setAnalystBusy(true); setAnalystError(""); setAnalystResult(null);
    try {
      const routed = await routeTransactionNote(analystQuestion.trim(), "reports");
      if (!routed) {
        const explicitPeriod = /\b(today|daily|this week|weekly|this month|monthly|this year|yearly|annual)\b/i.test(analystQuestion);
        setAnalystResult(await api.businessAnalysis(business.id, analystQuestion, explicitPeriod ? null : period));
      }
    }
    catch (e) { setAnalystError(e instanceof Error ? e.message : "Could not generate business analysis."); }
    finally { setAnalystBusy(false); }
  }

  function exportBusinessAnalysis() {
    if (!business || !analystResult) return;
    const html = `<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(business.name)} AI business analysis</title><style>body{font:15px Arial,sans-serif;max-width:900px;margin:36px auto;padding:0 20px;color:#1b2a20;line-height:1.6}h1{margin-bottom:4px}.meta{color:#536458}.answer{border-top:3px solid #83b94e;padding-top:20px}.answer h2,.answer h3,.answer h4{margin:1.2em 0 .5em}.answer ul,.answer ol{padding-left:24px}.answer hr{border:0;border-top:1px solid #b9c7bc;margin:20px 0}.answer code{background:#edf3ee;padding:2px 4px;border-radius:3px}.notice{background:#fff3dc;padding:14px;border-radius:8px;margin-top:24px}</style></head><body><h1>${escapeHtml(business.name)} · Business analysis</h1><p class="meta">${escapeHtml(analystResult.start_date)} to ${escapeHtml(analystResult.end_date)} · ${escapeHtml(analystResult.period)}</p><h2>${escapeHtml(analystResult.question)}</h2><div class="answer">${markdownToHtml(analystResult.answer, escapeHtml)}</div><p class="notice">${escapeHtml(analystResult.notice)} This is a management summary, not audited accounting advice.</p></body></html>`;
    downloadFile(`${business.name.replace(/[^a-z0-9-_]+/gi, "-")}-ai-business-analysis-${analystResult.start_date}.html`, html, "text/html;charset=utf-8");
  }

  function exportBusinessAnalysisCsv() {
    if (!business || !analystResult) return;
    const rows: Array<[string, unknown]> = [
      ["Business", business.name], ["Question", analystResult.question], ["Period", analystResult.period],
      ["Start date", analystResult.start_date], ["End date", analystResult.end_date],
      ["AI analysis", analystResult.answer],
    ];
    const flatten = (value: unknown, prefix = "Calculated data") => {
      if (value && typeof value === "object" && !Array.isArray(value)) {
        Object.entries(value as Record<string, unknown>).forEach(([key, child]) => flatten(child, `${prefix} / ${key}`));
      } else if (Array.isArray(value)) {
        rows.push([prefix, value.map(item => typeof item === "object" ? JSON.stringify(item) : String(item)).join("; ")]);
      } else rows.push([prefix, value]);
    };
    flatten(analystResult.calculated_data);
    const quote = (value: unknown) => `"${String(value ?? "").replaceAll('"', '""')}"`;
    const csv = ["Field,Value", ...rows.map(([key,value]) => `${quote(key)},${quote(value)}`)].join("\r\n");
    downloadFile(`${business.name.replace(/[^a-z0-9-_]+/gi, "-")}-ai-business-analysis-${analystResult.start_date}.csv`, "\uFEFF" + csv, "text/csv;charset=utf-8");
  }

  function openRecordModal(templateId?: string) {
    const nextId = templateId || templates[0]?.id || "";
    setSelectedTemplate(nextId); setRecordValues({date:new Date().toISOString().slice(0,10)}); setShowRecordModal(true);
  }

  async function createRecord(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!business || !selectedTemplate) return;
    setSaving(true); setError("");
    const template = templates.find(t => t.id === selectedTemplate);
    if (!template) return;
    const values: Record<string, unknown> = {};
    for (const [key, raw] of Object.entries(recordValues)) {
      if (raw === "") continue;
      const field = template.fields.find(f => (f.name || f.key) === key);
      const type = String(field?.type || "").toLowerCase();
      values[key] = ["number","integer","decimal","currency","money"].some(t => type.includes(t)) ? Number(raw) : raw;
    }
    try {
      await api.createRecord(business.id, template.id, values);
      setShowRecordModal(false); setNotice("Record saved successfully."); await load(business.id, period);
    } catch (e) { setError(e instanceof Error ? e.message : "Could not save record."); }
    finally { setSaving(false); }
  }

  async function saveProfile(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setProfileSaving(true); setError("");
    try {
      const updated = await api.updateProfile(profileName.trim());
      onUserUpdated(updated); setNotice("Profile updated successfully.");
    } catch (e) { setError(e instanceof Error ? e.message : "Could not update profile."); }
    finally { setProfileSaving(false); }
  }

  async function savePassword(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setProfileSaving(true); setError("");
    try {
      await api.changePassword(currentPassword, newPassword);
      setCurrentPassword(""); setNewPassword(""); setNotice("Password changed. Please sign in again with your new password.");
      setShowProfileModal(false); onLogout();
    } catch (e) { setError(e instanceof Error ? e.message : "Could not change password."); }
    finally { setProfileSaving(false); }
  }

  const selectedRecordTemplate = templates.find(t => t.id === selectedTemplate);
  const fieldName = (f: TemplateField) => String(f.name || f.key || "field");
  const fieldLabel = (f: TemplateField) => String(f.label || f.name || f.key || "Field").replaceAll("_", " ");
  const navItems = [
    {name:"Overview", icon:<LayoutDashboard size={18}/>},
    {name:"Records", icon:<BookOpen size={18}/>},
    {name:"Reports", icon:<BarChart3 size={18}/>},
  ];

  if (loading) return <div className="loading-screen"><div className="brand-mark"><Activity size={23}/></div><LoaderCircle className="spin" size={22}/><span>Preparing your workspace…</span></div>;

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><Activity size={22}/></div><div><strong>LedgerMind<span> AI</span></strong><small>BUSINESS INTELLIGENCE</small></div></div>
      <div className="workspace-label">WORKSPACE</div>
      {business ? <button className="business-switch" onClick={() => setShowBusinessModal(true)}><span className="business-avatar">{business.business_type === "restaurant" ? <Utensils size={17}/> : business.business_type === "trucking" ? <Truck size={17}/> : <Store size={17}/>}</span><span className="business-info"><b>{business.name}</b><small>{pretty(business.business_type)}</small></span><ChevronDown size={16}/></button> :
        <button className="business-switch empty-switch" onClick={() => setShowBusinessModal(true)}><span className="business-avatar"><Plus size={18}/></span><span className="business-info"><b>Add a business</b><small>Start your workspace</small></span><ChevronDown size={16}/></button>}
      <nav className="nav-list" aria-label="Main navigation">
        {navItems.map(item => <button key={item.name} className={`nav-item ${activeNav === item.name ? "active" : ""}`} onClick={() => setActiveNav(item.name)}>{item.icon}<span>{item.name}</span>{activeNav === item.name && <span className="nav-indicator"/>}</button>)}
      </nav>
      <div className="sidebar-bottom">
        <div className="security-note"><ShieldCheck size={18}/><div><b>Your records, clearly.</b><span>Evidence before assumptions.</span></div></div>
        <button className="user-profile account-trigger" onClick={() => {setProfileName(user.full_name);setShowProfileModal(true);}}><div className="user-avatar">{user.full_name.slice(0,1).toUpperCase()}</div><div><b>{user.full_name}</b><small>{user.email}</small></div><UserRound size={17}/></button>
      </div>
    </aside>

    <main className="main-content">
      <header className="topbar">
        <div className="breadcrumbs"><span>Workspace</span><span className="crumb-separator">/</span><b>{activeNav}</b></div>
        <div className="top-actions">
          <span className={`api-status ${apiOnline ? "online" : "offline"}`}><span/>{apiOnline ? "API connected" : "API offline"}</span>
          <button className="icon-button" onClick={() => void load()} title="Refresh data" aria-label="Refresh data"><RefreshCw size={17} className={refreshing ? "spin" : ""}/></button>
          <button className="icon-button" onClick={() => {setProfileName(user.full_name);setShowProfileModal(true);}} title="Account profile" aria-label="Account profile"><UserRound size={17}/></button>
          <button className="primary-button compact" onClick={() => business ? openRecordModal() : setShowBusinessModal(true)}><Plus size={17}/> New record</button>
        </div>
      </header>

      <div className="page-wrap">
        {error && <div className="alert error-alert"><AlertCircle size={18}/><span>{error}</span><button onClick={() => setError("")} aria-label="Dismiss"><X size={16}/></button></div>}
        {notice && <div className="alert success-alert"><Check size={18}/><span>{notice}</span><button onClick={() => setNotice("")} aria-label="Dismiss"><X size={16}/></button></div>}

        {!business ? <section className="welcome-panel">
          <div className="welcome-copy"><span className="eyebrow"><span className="eyebrow-dot"/> YOUR BUSINESS, IN FOCUS</span><h1>Good records.<br/><em>Clearer decisions.</em></h1><p>Bring your daily business activity into one place. Track records, understand your numbers, and review differences with the evidence in front of you.</p><button className="primary-button" onClick={() => setShowBusinessModal(true)}><Plus size={18}/> Set up your business</button><div className="welcome-foot"><ShieldCheck size={16}/> You stay in control of your records.</div></div>
          <div className="welcome-graphic"><div className="graphic-glow"/><div className="report-preview"><div className="preview-top"><span>BUSINESS SNAPSHOT</span><span className="preview-dot"/></div><div className="preview-label">Sales revenue</div><div className="preview-number">₦ ———</div><div className="preview-chart"><span/><span/><span/><span/><span/><span/><span/><span/><span/><span/><span/><span/></div><div className="preview-line"><span/><span/><span/></div></div><div className="float-chip chip-one"><ArrowUpRight size={16}/> Clearer trends</div><div className="float-chip chip-two"><ShieldCheck size={16}/> Evidence-led</div></div>
        </section> : <>
          <section className="page-heading">
            <div><span className="eyebrow"><span className="eyebrow-dot"/> {activeNav === "Reports" ? "BUSINESS INTELLIGENCE" : activeNav === "Records" ? "RECORDS MANAGEMENT" : "BUSINESS OVERVIEW"}</span><h1>{activeNav === "Records" ? "Your records" : activeNav === "Reports" ? "Reports & insights" : "Good to see you."}</h1><p>{activeNav === "Records" ? "Every entry in one place, ready to review." : activeNav === "Reports" ? "Understand the numbers behind your day-to-day." : "Here’s what your records say for this period."}</p></div>
            <div className="heading-actions"><label className="period-select"><Clock3 size={16}/><select value={period} onChange={e => {setPeriod(e.target.value);setAnalystResult(null);}}><option value="daily">Today</option><option value="weekly">This week</option><option value="monthly">This month</option><option value="yearly">This year</option></select><ChevronDown size={14}/></label><button className="primary-button" onClick={() => openRecordModal()}><Plus size={17}/> Add record</button></div>
          </section>

          {activeNav === "Records" && <section className="panel investigator-panel" style={{marginBottom: "22px", padding: "22px"}} aria-labelledby="ai-review-title">
            <div className="panel-head"><div><h2 id="ai-review-title">LedgerMind Investigator</h2><p>Interpret invoices and payment notes, review extracted details, and save confirmed supplier invoices.</p></div><span className="status-pill review">Human review required</span></div>
            <form onSubmit={interpretNote} className="form-stack">
              <label>Invoice or payment note<textarea className="ai-note-input" rows={3} maxLength={20000} required minLength={5} value={aiNote} onChange={e => setAiNote(e.target.value)} placeholder="Describe an invoice or payment note…" /></label>
              <div style={{display:"flex",gap:8,flexWrap:"wrap"}}><button className="primary-button" type="submit" disabled={aiBusy}>{aiBusy ? <LoaderCircle size={16} className="spin"/> : <Activity size={16}/>} {aiBusy ? "Interpreting…" : "Interpret note"}</button><button className="secondary-button" type="button" onClick={startVoiceInput} disabled={voiceListening}>{voiceListening ? <MicOff size={16}/> : <Mic size={16}/>} {voiceListening ? "Listening…" : "Speak note"}</button></div>
            </form>
            {aiError && <div className="alert error-alert" style={{marginTop:12}}><AlertCircle size={17}/><span>{aiError}</span></div>}
            {aiResult && <div className="ai-review-result" style={{marginTop:16,border:"1px solid var(--border, #dbe3ea)",borderRadius:14,padding:18,background:"#18231c",color:"#e5eee6"}}>
              <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",gap:12,flexWrap:"wrap",marginBottom:14}}>
                <div><span className="status-pill review">Review before saving</span><h3 style={{margin:"10px 0 4px",fontSize:20}}>{String(aiResult.party_name || "Unknown supplier or party")}</h3><p style={{margin:0,color:"#a9b9ac"}}>{pretty(String(aiResult.transaction_type || "unknown"))}{aiResult.reference ? ` · ${String(aiResult.reference)}` : ""}</p></div>
                <div className="ai-export-actions">
                  <button type="button" className="secondary-button export-button" onClick={exportAiAnalysisCsv} title="Download the current AI analysis as a spreadsheet"><FileSpreadsheet size={15}/> Spreadsheet</button>
                  <button type="button" className="secondary-button export-button" onClick={exportAiAnalysisDocument} title="Download a formatted report of the current AI analysis"><FileText size={15}/> Document</button>
                  <button type="button" className="secondary-button" onClick={() => setAiResult(null)}>Clear result</button>
                </div>
              </div>
              <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(150px,1fr))",gap:10}}>
                <div style={{padding:12,borderRadius:10,background:"#202d24",color:"#e5eee6",border:"1px solid #354638"}}><small style={{color:"#a9b9ac"}}>Invoice amount</small><div style={{fontSize:21,fontWeight:700,marginTop:4}}>{aiResult.invoice_amount == null ? "Not provided" : money(Number(aiResult.invoice_amount), business?.currency || "NGN")}</div></div>
                <div style={{padding:12,borderRadius:10,background:"#202d24",color:"#e5eee6",border:"1px solid #354638"}}><small style={{color:"#a9b9ac"}}>Amount paid</small><div style={{fontSize:21,fontWeight:700,marginTop:4}}>{aiResult.amount_paid == null ? "Not provided" : money(Number(aiResult.amount_paid), business?.currency || "NGN")}</div></div>
                <div style={{padding:12,borderRadius:10,background:"#202d24",color:"#e5eee6",border:"1px solid #354638"}}><small style={{color:"#a9b9ac"}}>Outstanding (calculated)</small><div style={{fontSize:21,fontWeight:700,marginTop:4}}>{aiResult.invoice_amount == null || aiResult.amount_paid == null ? "Needs review" : money(Math.max(0, Number(aiResult.invoice_amount) - Number(aiResult.amount_paid)), business?.currency || "NGN")}</div></div>
              </div>
              <div className="field-grid" style={{marginTop:16}}>
                <label>Supplier / party<input value={String(aiResult.party_name || "")} onChange={event=>updateAiField("party_name",event.target.value)} /></label>
                <label>Invoice amount<input type="number" min="0" step="0.01" value={aiResult.invoice_amount == null ? "" : String(aiResult.invoice_amount)} onChange={event=>updateAiField("invoice_amount",event.target.value === "" ? null : Number(event.target.value))}/></label>
                <label>Amount paid<input type="number" min="0" step="0.01" value={aiResult.amount_paid == null ? "" : String(aiResult.amount_paid)} onChange={event=>updateAiField("amount_paid",event.target.value === "" ? null : Number(event.target.value))}/></label>
                <label>Transaction date<input type="date" value={String(aiResult.transaction_date || "")} onChange={event=>updateAiField("transaction_date",event.target.value || null)}/></label>
                <label>Reference<input value={String(aiResult.reference || "")} onChange={event=>updateAiField("reference",event.target.value)}/></label>
                <label>Who owes whom?<select value={String(aiResult.direction || "unknown")} onChange={event=>updateAiField("direction",event.target.value)}><option value="business_owes_party">Business owes supplier</option><option value="party_owes_business">Supplier owes business</option><option value="unknown">Unknown</option></select></label>
                <label className="full-field">Review note<textarea rows={2} value={String(aiResult.note || "")} onChange={event=>updateAiField("note",event.target.value)}/></label>
              </div>
              {Array.isArray(aiResult.missing_information) && aiResult.missing_information.length > 0 && <div className="alert" style={{marginBottom:10}}><AlertCircle size={16}/><span><strong>Missing information:</strong> {aiResult.missing_information.map(String).join(", ")}</span></div>}
              {Array.isArray(aiResult.ambiguity) && aiResult.ambiguity.length > 0 && <div className="alert" style={{marginBottom:10}}><AlertCircle size={16}/><span><strong>Needs clarification:</strong> {aiResult.ambiguity.map(String).join("; ")}</span></div>}
              {typeof aiResult.note === "string" && aiResult.note.trim() !== "" && <p style={{margin:"12px 0",lineHeight:1.5}}><strong>Note:</strong> {aiResult.note}</p>}
              <div style={{display:"flex",gap:8,flexWrap:"wrap",marginTop:12}}>
                <button type="button" className="primary-button" onClick={()=>void saveReviewedInvoice()} disabled={invoiceSaving}>{invoiceSaving ? <LoaderCircle size={16} className="spin"/> : <Save size={16}/>} {invoiceSaving ? "Saving invoice…" : "Confirm and save invoice"}</button>
                <button type="button" className="secondary-button" onClick={continueAsBusinessRecord}><Save size={16}/> Continue as business record</button>
              </div>
              <p className="recon-foot"><ShieldCheck size={15}/> This is an AI-generated review preview, not a saved record or proof of payment. Confirm the details before saving. The outstanding amount above is calculated by LedgerMind's interface from the extracted amounts.</p>
            </div>}
          </section>}

          {activeNav === "Overview" && <section className="panel overview-assistant-panel" style={{marginBottom:22,padding:22}} aria-labelledby="overview-assistant-title">
            <div className="panel-head"><div><h2 id="overview-assistant-title"><BrainCircuit size={18} style={{verticalAlign:"middle",marginRight:8}}/>LedgerMind Assistant</h2><p>Ask general business questions or request guidance. Answers use the selected business context where relevant.</p></div><span className="status-pill balanced">Business assistant</span></div>
            <form className="form-stack" onSubmit={async event => { event.preventDefault(); if (!business || !overviewQuestion.trim()) return; setOverviewBusy(true); setOverviewError(""); setOverviewAnswer(null); try { const routed = await routeTransactionNote(overviewQuestion.trim(), "overview"); if (!routed) setOverviewAnswer(await api.businessAnalysis(business.id, overviewQuestion.trim(), null)); } catch (e) { setOverviewError(e instanceof Error ? e.message : "Could not answer your question."); } finally { setOverviewBusy(false); } }}>
              <label>Ask LedgerMind<textarea className="assistant-input" rows={3} maxLength={2000} minLength={3} required value={overviewQuestion} onChange={event=>setOverviewQuestion(event.target.value)} placeholder="Ask about running your business, managing stock, improving sales, or understanding your records…" /></label>
              <div className="assistant-actions"><button className="primary-button" disabled={overviewBusy || !overviewQuestion.trim()}>{overviewBusy ? <LoaderCircle size={16} className="spin"/> : <BrainCircuit size={16}/>} {overviewBusy ? "Preparing answer…" : "Ask LedgerMind"}</button><button type="button" className="secondary-button" onClick={startOverviewVoiceInput} disabled={overviewBusy || overviewVoiceListening}>{overviewVoiceListening ? <MicOff size={16}/> : <Mic size={16}/>} {overviewVoiceListening ? "Listening…" : "Speak question"}</button></div>
            </form>
            {overviewError && <div className="alert error-alert" style={{marginTop:12}}><AlertCircle size={17}/><span>{overviewError}</span></div>}
            {overviewAnswer && <article className="analyst-result markdown-result" style={{marginTop:16,padding:18,borderRadius:12,border:"1px solid #354638",background:"#18231c",color:"#e5eee6"}}><div className="panel-head"><div><h3>LedgerMind Assistant</h3><p>Response for {business.name}</p></div></div>{renderMarkdown(overviewAnswer.answer)}<p className="recon-foot"><ShieldCheck size={15}/>{overviewAnswer.notice}</p></article>}
          </section>}

          {activeNav === "Overview" && <section className="panel intelligence-panel" aria-labelledby="intelligence-title">
            <div className="panel-head">
              <div><h2 id="intelligence-title">Issues to review</h2><p>Evidence-based checks on saved records; findings are prompts for review, not accusations.</p></div>
              <span className={`status-pill ${intelligenceIssues.some(issue => issue.severity === "review") ? "review" : "balanced"}`}>{intelligenceIssues.length ? `${intelligenceIssues.length} finding${intelligenceIssues.length === 1 ? "" : "s"}` : "No flags"}</span>
            </div>
            <div className="intelligence-summary">
              <div><strong>{intelligenceIssues.filter(issue => issue.severity === "review").length}</strong><span>Needs review</span></div>
              <div><strong>{intelligenceIssues.filter(issue => issue.severity === "info").length}</strong><span>Informational</span></div>
            </div>
            {intelligenceIssues.length ? <div className="intelligence-list">
              {intelligenceIssues.map((issue, index) => <article className="intelligence-item" key={`${issue.type}-${issue.record_ids.join("-")}-${index}`}>
                <span className={`intelligence-mark ${issue.severity === "review" ? "needs-review" : "informational"}`}><AlertCircle size={17}/></span>
                <div className="intelligence-copy"><div className="intelligence-item-head"><b>{issue.title}</b><span className={`status-pill ${issue.severity === "review" ? "review" : "balanced"}`}>{pretty(issue.severity)}</span></div><p>{issue.message}</p><small>Evidence: {issue.record_ids.length} affected record{issue.record_ids.length === 1 ? "" : "s"} · IDs {issue.record_ids.map(id => id.slice(0, 8)).join(", ")}</small></div>
              </article>)}
            </div> : <div className="intelligence-empty"><ShieldCheck size={20}/><b>No review flags detected</b><span>{intelligenceNotice || "The current saved records did not trigger the configured checks."}</span></div>}
            {intelligenceIssues.length > 0 && <p className="intelligence-notice"><ShieldCheck size={14}/>{intelligenceNotice || "Confirm each finding against source documents before taking action."}</p>}
          </section>}

          {activeNav !== "Records" && <section className="stats-grid">
            <StatCard label="Sales revenue" value={money(sales,business.currency)} note={salesChange === null || salesChange === undefined ? "No previous sales baseline" : `${salesChange >= 0 ? "+" : ""}${salesChange.toFixed(1)}% vs previous period`} icon={<ArrowUpRight size={18}/>}/>
            <StatCard label="Operating expenses" value={money(expenses,business.currency)} note="Recorded expenses in period" icon={<Wallet size={18}/>}/>
            <StatCard label="Purchases" value={money(purchases,business.currency)} note="Purchases recorded separately" icon={<ArrowDownRight size={18}/>}/>
            <StatCard label="Records in period" value={totalRecords.toLocaleString("en-NG")} note="Entries included in this report" icon={<BookOpen size={18}/>}/>
          </section>}

          {activeNav !== "Records" && activeNav === "Reports" && <section className="panel analyst-panel" style={{marginBottom:22,padding:22}} aria-labelledby="analyst-title">
            <div className="panel-head"><div><h2 id="analyst-title"><BrainCircuit size={18} style={{verticalAlign:"middle",marginRight:8}}/>LedgerMind Business Analyst</h2><p>Analyze calculated data from this business and reporting period.</p></div><span className="status-pill balanced">Database-grounded</span></div>
            <form className="form-stack" onSubmit={runBusinessAnalysis}>
              <label>Ask about your business<textarea rows={3} maxLength={2000} minLength={5} required value={analystQuestion} onChange={event=>setAnalystQuestion(event.target.value)} placeholder="Ask a question about this reporting period, for example: Summarize sales and expenses for this month…"/></label>
              <div className="assistant-actions"><button className="primary-button" disabled={analystBusy}>{analystBusy ? <LoaderCircle size={16} className="spin"/> : <BrainCircuit size={16}/>} {analystBusy ? "Analyzing saved data…" : "Analyze business data"}</button>{analystResult && <><button type="button" className="secondary-button" onClick={exportBusinessAnalysisCsv}><FileSpreadsheet size={15}/> Spreadsheet</button><button type="button" className="secondary-button" onClick={exportBusinessAnalysis}><FileText size={15}/> Document</button></>}</div>
            </form>
            {analystError && <div className="alert error-alert" style={{marginTop:12}}><AlertCircle size={17}/><span>{analystError}</span></div>}
            {analystResult && <article className="analyst-result" style={{marginTop:16,padding:18,borderRadius:12,border:"1px solid #354638",background:"#18231c",color:"#e5eee6"}}><div className="panel-head"><div><h3>{analystResult.start_date} — {analystResult.end_date}</h3><p>Based on calculated records for {business.name}</p></div></div><div className="markdown-result">{renderMarkdown(analystResult.answer)}</div><p className="recon-foot"><ShieldCheck size={15}/> {analystResult.notice}</p></article>}
            {report?.supplier_invoice_summary && <div className="stats-grid" style={{marginTop:16}}><StatCard label="Supplier invoices" value={String(report.supplier_invoice_summary.invoice_count)} note="Confirmed invoices in period" icon={<FileText size={18}/>}/><StatCard label="Invoice totals" value={money(report.supplier_invoice_summary.invoice_total,business.currency)} note="Separate from generic purchases" icon={<Wallet size={18}/>}/><StatCard label="Paid against invoices" value={money(report.supplier_invoice_summary.amount_paid,business.currency)} note="Recorded on saved invoices" icon={<Check size={18}/>}/><StatCard label="Outstanding invoices" value={money(report.supplier_invoice_summary.outstanding_balance,business.currency)} note="Calculated from saved invoices" icon={<AlertCircle size={18}/>}/></div>}
          </section>}

          {activeNav !== "Records" && <>{report && <section className="insight-grid">
            <article className="panel revenue-panel">
              <div className="panel-head"><div><h2>Activity over time</h2><p>Sales and operating expenses by date</p></div><span className="period-badge">{report.start_date} — {report.end_date}</span></div>
              {report.daily_breakdown.length ? <div className="activity-chart" role="img" aria-label="Daily sales and operating expenses bar chart">
                {report.daily_breakdown.slice(-14).map(day => {
                  const max = Math.max(1, ...report.daily_breakdown.map(d => Math.max(d.sales_revenue,d.operating_expenses)));
                  const h = Math.max(3, day.sales_revenue / max * 100);
                  const eh = day.operating_expenses ? Math.max(3,day.operating_expenses / max * 100) : 2;
                  return <div className="chart-column" key={day.date} title={`${day.date}: sales ${money(day.sales_revenue,business.currency)}, expenses ${money(day.operating_expenses,business.currency)}`}><div className="bar-pair"><span className="bar sales-bar" style={{height:`${h}%`}}/><span className="bar expense-bar" style={{height:`${eh}%`}}/></div><small>{day.date.slice(8)}</small></div>;
                })}
              </div> : <div className="empty-chart"><div className="empty-chart-icon"><BarChart3 size={23}/></div><b>No activity for this period yet</b><span>Add records to start building your business history.</span></div>}
              <div className="chart-legend"><span><i className="legend-sales"/>Sales</span><span><i className="legend-expenses"/>Expenses</span><small>Values from saved records</small></div>
            </article>
            <article className="panel reconciliation-panel">
              <div className="panel-head"><div><h2>Reconciliation</h2><p>Sales vs recorded incoming payments</p></div><span className={`status-pill ${report.reconciliation.status === "matches" ? "balanced" : "review"}`}>{report.reconciliation.status === "matches" ? "Balanced" : "Review"}</span></div>
              <div className="recon-amount">{money(Math.abs(reconciliationDifference),business.currency)}</div>
              <p className="recon-caption">{reconciliationDifference === 0 ? "No difference between these totals." : reconciliationDifference > 0 ? "Sales exceed recorded incoming payments." : "Incoming payments exceed recorded sales."}</p>
              <div className="recon-detail"><AlertCircle size={17}/><span>{report.reconciliation.interpretation}</span></div>
              <div className="recon-foot"><ShieldCheck size={15}/>{report.reconciliation.warning}</div>
            </article>
          </section>}</>}

          {activeNav === "Records" && <section className="panel" style={{marginBottom:22,padding:22}}><div className="panel-head"><div><h2>Supplier invoices</h2><p>Confirmed invoice records for this business, including calculated outstanding balances.</p></div><span className="template-count">{supplierInvoices.length}</span></div>{supplierInvoices.length ? <div className="table-wrap"><table><thead><tr><th>Supplier</th><th>Date</th><th>Reference</th><th>Invoice total</th><th>Paid</th><th>Outstanding</th></tr></thead><tbody>{supplierInvoices.map(invoice=><tr key={invoice.id}><td><b>{invoice.supplier}</b><small className="record-subtitle">{invoice.note || "Supplier invoice"}</small></td><td>{invoice.transaction_date}</td><td>{invoice.reference || "—"}</td><td className="amount-cell">{money(Number(invoice.invoice_amount),business.currency)}</td><td>{money(Number(invoice.amount_paid),business.currency)}</td><td className="amount-cell">{money(Number(invoice.outstanding_amount),business.currency)}</td></tr>)}</tbody></table></div> : <div className="empty-records"><FileText size={22}/><b>No supplier invoices saved</b><span>Open LedgerMind Investigator above to interpret an invoice, review the extracted fields, and confirm Save invoice.</span><button className="text-button" onClick={()=>setActiveNav("Records")}>Open LedgerMind Investigator</button></div>}</section>}

          {activeNav !== "Reports" && <section className="lower-grid">
            <article className="panel records-panel">
              <div className="panel-head records-export-head"><div><h2>{activeNav === "Records" ? "Business records" : "Recent records"}</h2><p>Latest entries captured for this business</p></div><div className="records-export-actions"><button className="secondary-button export-button" onClick={exportRecordsCsv} title="Download saved records as CSV"><FileSpreadsheet size={15}/> Spreadsheet</button><button className="secondary-button export-button" onClick={exportRecordsDocument} title="Download saved records as a formatted document"><FileText size={15}/> Document</button><button className="text-button" onClick={() => setActiveNav("Records")}>View records <ArrowUpRight size={15}/></button></div></div>
              <div className="records-toolbar"><div className="search-box"><Search size={16}/><input placeholder="Search records…" value={query} onChange={e => setQuery(e.target.value)}/></div><span>{filteredRecords.length} total</span></div>
              {filteredRecords.length ? <div className="table-wrap"><table><thead><tr><th>Record</th><th>Date</th><th>Amount</th><th>Saved</th></tr></thead><tbody>{(activeNav === "Records" ? filteredRecords : filteredRecords.slice(0,8)).map(record => {
                const template = templates.find(t => t.id === record.template_id);
                return <tr key={record.id}><td><span className="record-icon"><FilePlus2 size={16}/></span><span className="record-title"><b>{template?.name || "Business record"}</b><small>{String(record.values.notes || record.values.description || record.id.slice(0,8))}</small></span></td><td>{valueDate(record).slice(0,10) || "—"}</td><td className="amount-cell">{money(recordAmount(record),business.currency)}</td><td>{new Date(record.created_at).toLocaleDateString("en-NG",{day:"2-digit",month:"short"})}</td></tr>;
              })}</tbody></table></div> : <div className="empty-records"><BookOpen size={22}/><b>No records found</b><span>Try another search or add your first record.</span><button className="text-button" onClick={() => openRecordModal()}><Plus size={15}/> Add a record</button></div>}
            </article>
            {activeNav === "Overview" && <article className="panel templates-panel">
              <div className="panel-head"><div><h2>Record templates</h2><p>Built for {pretty(business.business_type)}s</p></div><span className="template-count">{templates.length}</span></div>
              <div className="template-list">{templates.map(template => <button className="template-row" key={template.id} onClick={() => openRecordModal(template.id)}><span className="template-icon">{template.key.includes("sales") ? <Wallet size={17}/> : template.key.includes("stock") || template.key.includes("product") ? <Store size={17}/> : template.key.includes("expense") || template.key.includes("purchase") ? <ArrowDownRight size={17}/> : <BookOpen size={17}/>}</span><span className="template-copy"><b>{template.name}</b><small>{template.description}</small></span><Plus size={16} className="template-plus"/></button>)}</div>
            </article>}
          </section>}
          <section className="footnote-row"><ShieldCheck size={15}/><span>Reports summarize recorded information; they are not audited accounts or proof of wrongdoing.</span><span className="footnote-spacer"/><span>Timezone: {business.timezone}</span></section>
        </>}
      </div>
    </main>

    {showProfileModal && <Modal title="Your account" onClose={() => setShowProfileModal(false)}><div className="form-stack">
      <div className="profile-summary"><div className="profile-avatar-large">{user.full_name.slice(0,1).toUpperCase()}</div><div><b>{user.full_name}</b><span><Mail size={13}/>{user.email}</span><small>Member since {new Date(user.created_at).toLocaleDateString("en-NG", {day:"numeric", month:"short", year:"numeric"})}</small></div></div>
      <form className="form-stack profile-form" onSubmit={saveProfile}><label>Full name<input required minLength={2} maxLength={120} value={profileName} onChange={e => setProfileName(e.target.value)}/></label><button className="primary-button form-submit" disabled={profileSaving}><Check size={16}/> Save profile</button></form>
      <div className="profile-section-title"><KeyRound size={15}/> Change password</div>
      <form className="form-stack profile-form" onSubmit={savePassword}><label>Current password<input type="password" required autoComplete="current-password" value={currentPassword} onChange={e => setCurrentPassword(e.target.value)}/></label><label>New password<input type="password" required minLength={10} maxLength={128} autoComplete="new-password" value={newPassword} onChange={e => setNewPassword(e.target.value)} placeholder="At least 10 characters"/></label><button className="secondary-button form-submit" disabled={profileSaving}>Change password and sign out</button></form>
      <button className="logout-button" onClick={onLogout}><LogOut size={16}/> Sign out of LedgerMind AI</button>
    </div></Modal>}

    {showBusinessModal && <Modal title="Your workspaces" onClose={() => setShowBusinessModal(false)}><div className="form-stack">
      <p className="modal-intro">Choose a business to open, or create another workspace. Each business keeps its own records and reports.</p>
      {businesses.length > 0 && <div className="workspace-list">
        {businesses.map(item => <button type="button" key={item.id} className={`workspace-option ${business?.id === item.id ? "workspace-option-active" : ""}`} onClick={() => { setShowBusinessModal(false); void load(item.id, period); }}>
          <span className="business-avatar">{item.business_type === "restaurant" ? <Utensils size={17}/> : item.business_type === "trucking" ? <Truck size={17}/> : <Store size={17}/>}</span>
          <span className="business-info"><b>{item.name}</b><small>{pretty(item.business_type)}</small></span>
          {business?.id === item.id ? <Check size={17}/> : <ChevronDown size={16}/>}
        </button>)}
      </div>}
      <div className="workspace-create-heading"><span>Create a new business</span></div>
      <form className="form-stack workspace-create-form" onSubmit={createBusiness}>
      <label>Business name<input autoFocus required minLength={2} maxLength={160} value={businessName} onChange={e => setBusinessName(e.target.value)} placeholder="e.g. The Green Plate"/></label>
      <label>Country of operation<select value={businessCountry} onChange={e => {const code=e.target.value; const item=countryOptions.find(country=>country.code===code)!; setBusinessCountry(code); const browserTz=Intl.DateTimeFormat().resolvedOptions().timeZone; setBusinessTimezone(item.timezones.length > 1 ? browserTz : item.timezones[0]);}}>{countryOptions.map(item=><option key={item.code} value={item.code}>{item.name} · {item.currency}</option>)}</select></label>
      <label>Business time zone<select value={businessTimezone} onChange={e=>setBusinessTimezone(e.target.value)}>{Array.from(new Set([...(countryOptions.find(item=>item.code===businessCountry)?.timezones || ["UTC"]), ...(countryOptions.find(item=>item.code===businessCountry)?.timezones.length! > 1 ? [businessTimezone] : [])])).map(zone=><option key={zone} value={zone}>{zone}</option>)}</select><small>Confirm the time zone used for business dates and reporting.</small></label>
      <label>Business type<select value={businessType} onChange={e => setBusinessType(e.target.value as BusinessType)}><option value="restaurant">Restaurant</option><option value="supermarket">Supermarket</option><option value="trucking">Transport / Trucking</option><option value="contractor">Contractor</option><option value="hotel">Hotel</option><option value="farm">Farm</option><option value="rental_property">Rental Property</option><option value="school">School</option><option value="salon">Salon</option><option value="training">Training / Courses</option><option value="pharmacy">Pharmacy</option></select></label>
      {businessType === "farm" && <fieldset className="farm-module-options"><legend>Farm modules</legend><p>Select every operation this farm runs. Shared farm records are included automatically.</p>{(["crops", "livestock", "poultry"] as const).map(module => <label key={module}><input type="checkbox" checked={farmModules.includes(module)} onChange={e => setFarmModules(current => e.target.checked ? [...current, module] : current.filter(item => item !== module))}/>{module === "crops" ? "Crops" : module === "livestock" ? "Livestock" : "Poultry"}</label>)}</fieldset>}
      <div className="business-type-note"><Store size={18}/><span>{businessType === "farm" ? "Shared farm register and cashbook, plus templates for only the modules selected above." : `Starter templates for ${businessType.replace("_", " ")} operations.`}</span></div>
      <button className="primary-button form-submit" disabled={saving}>{saving ? <LoaderCircle size={17} className="spin"/> : <Plus size={17}/>} Create business</button>
      </form>
    </div></Modal>}

    {showRecordModal && selectedRecordTemplate && <Modal title={`Add ${selectedRecordTemplate.name.toLowerCase()}`} onClose={() => setShowRecordModal(false)}><form className="form-stack" onSubmit={createRecord}>
      <p className="modal-intro">{selectedRecordTemplate.description}</p>
      <label>Record template<select value={selectedTemplate} onChange={e => {setSelectedTemplate(e.target.value);setRecordValues({date:new Date().toISOString().slice(0,10)});}}>{templates.map(t => <option value={t.id} key={t.id}>{t.name}</option>)}</select></label>
      <div className="field-grid">{selectedRecordTemplate.fields.map(field => {
        const key = fieldName(field);
        const type = String(field.type || "text").toLowerCase();
        const label = fieldLabel(field);
        const required = Boolean(field.required);
        const value = recordValues[key] ?? "";
        const inputType = type.includes("date") ? "date" : ["number","integer","decimal","currency","money"].some(t => type.includes(t)) ? "number" : "text";
        const options = Array.isArray(field.options) ? field.options.map(String) : [];
        return <label key={key} className={type.includes("textarea") ? "full-field" : ""}>{label}{options.length ? <select required={required} value={value} onChange={e => setRecordValues(p => ({...p,[key]:e.target.value}))}><option value="">Select {label.toLowerCase()}</option>{options.map(o => <option key={o}>{o}</option>)}</select> : <input type={inputType} step={inputType === "number" ? "any" : undefined} required={required} value={value} onChange={e => setRecordValues(p => ({...p,[key]:e.target.value}))} placeholder={label}/>}</label>;
      })}</div>
      <div className="form-hint"><AlertCircle size={15}/> Only fields defined by this template can be saved. You can review the record after submission.</div>
      <button className="primary-button form-submit" disabled={saving}>{saving ? <LoaderCircle size={17} className="spin"/> : <Check size={17}/>} Save record</button>
    </form></Modal>}
  </div>;
}


export default function App() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [authLoading, setAuthLoading] = useState(true);

  useEffect(() => {
    const handleUnauthorized = () => { setAuthToken(""); setUser(null); };
    window.addEventListener("ledgermind:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("ledgermind:unauthorized", handleUnauthorized);
  }, []);

  useEffect(() => {
    const token = sessionStorage.getItem("ledgermind.sessionToken") || "";
    setAuthToken(token);
    if (!token) { setAuthLoading(false); return; }
    let active = true;
    api.me().then(profile => { if (active) setUser(profile); }).catch(() => {
      setAuthToken("");
      if (active) setUser(null);
    }).finally(() => { if (active) setAuthLoading(false); });
    return () => { active = false; };
  }, []);

  function authenticated(profile: UserProfile) { setUser(profile); }
  async function signOut() {
    try { await api.logout(); } catch { /* Clear local credentials even if the API is unavailable. */ }
    setAuthToken("");
    localStorage.removeItem(savedBusinessKey);
    setUser(null);
  }

  if (authLoading) return <div className="loading-screen"><div className="brand-mark"><Activity size={23}/></div><LoaderCircle className="spin" size={22}/><span>Securing your workspace…</span></div>;
  if (!user) return <AuthScreen onAuthenticated={authenticated}/>;
  return <Dashboard user={user} onLogout={() => { void signOut(); }} onUserUpdated={setUser}/>;
}
