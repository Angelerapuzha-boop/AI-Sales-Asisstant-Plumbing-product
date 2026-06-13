import { useState, useRef, useEffect } from "react";

// ─── PRODUCT CATALOG ────────────────────────────────────────────────────────
const INITIAL_PRODUCTS = [
  // PIPES
  { id:1, name:'PEX Pipe 1/2" × 10ft', category:"Pipes", price:24.99, unit:"roll", sku:"PEX-050-10", inStock:true,
    desc:'Flexible PEX-B tubing for hot/cold water distribution. Freeze-resistant and easy to install without soldering.',
    specs:'1/2" dia | 160 PSI | Max 180°F | PEX-B material | NSF-61' },
  { id:2, name:'PEX Pipe 3/4" × 10ft', category:"Pipes", price:34.99, unit:"roll", sku:"PEX-075-10", inStock:true,
    desc:'Larger diameter PEX-B for main supply lines and high-flow applications. Kink-resistant with lifetime flexibility.',
    specs:'3/4" dia | 160 PSI | Max 180°F | PEX-B material | NSF-61' },
  { id:3, name:'Copper Pipe Type L 1/2" × 10ft', category:"Pipes", price:42.99, unit:"stick", sku:"COP-L-050-10", inStock:true,
    desc:'Type L copper pipe for residential and commercial water supply. Thicker walls than Type M for added durability.',
    specs:'1/2" dia | Type L | 10ft length | Lead-free | NSF certified' },
  { id:4, name:'PVC Schedule 40 Pipe 1" × 10ft', category:"Pipes", price:12.99, unit:"stick", sku:"PVC-40-100-10", inStock:true,
    desc:'Standard Schedule 40 PVC for drain, waste, and vent (DWV) systems. UV-stable white finish.',
    specs:'1" dia | Schedule 40 | White | 10ft | ASTM D1785' },
  { id:5, name:'CPVC Pipe 1/2" × 10ft', category:"Pipes", price:19.99, unit:"stick", sku:"CPVC-050-10", inStock:true,
    desc:'Chlorinated PVC rated for hot water supply up to 200°F. Direct replacement for copper in hot water lines.',
    specs:'1/2" dia | CTS sizing | Max 200°F | NSF-61 | ASTM F441' },

  // FITTINGS
  { id:6, name:'SharkBite Push-Connect Elbow 1/2"', category:"Fittings", price:8.49, unit:"each", sku:"SB-ELB-050", inStock:true,
    desc:'No-solder, no-crimp 90° elbow. Works with PEX, copper, CPVC, and PE-RT. Removable with disconnect clip.',
    specs:'1/2" | 90° elbow | Lead-free brass | 200 PSI | ASSE 1061' },
  { id:7, name:'SharkBite Push-Connect Tee 1/2"', category:"Fittings", price:9.99, unit:"each", sku:"SB-TEE-050", inStock:true,
    desc:'Push-to-connect tee for branching water lines. Install in seconds without tools or pipe preparation.',
    specs:'1/2" | 3-way tee | Lead-free brass | 200 PSI | ASSE 1061' },
  { id:8, name:'SharkBite Coupling 1/2"', category:"Fittings", price:6.49, unit:"each", sku:"SB-COP-050", inStock:true,
    desc:'Straight coupling for joining two pipe sections. Ideal for repairs without torches or special tools.',
    specs:'1/2" | Straight coupling | Lead-free brass | 200 PSI' },
  { id:9, name:'Copper 90° Elbow 1/2" (C×C)', category:"Fittings", price:2.99, unit:"each", sku:"CU-ELB-050", inStock:true,
    desc:'Sweat-type copper elbow for soldered connections. Industry standard for permanent copper installations.',
    specs:'1/2" | 90° elbow | C×C sweat | Lead-free | ASTM B16.18' },
  { id:10, name:'PVC Sanitary Tee 3"×3"×3"', category:"Fittings", price:7.49, unit:"each", sku:"PVC-ST-300", inStock:true,
    desc:'Schedule 40 PVC sanitary tee for drain, waste, and vent piping systems.',
    specs:'3" all ports | DWV | Schedule 40 | White | Hub ends' },

  // VALVES
  { id:11, name:'Ball Valve 1/2" Full Port Lead-Free', category:"Valves", price:18.99, unit:"each", sku:"BV-FP-050", inStock:true,
    desc:'Full-port brass ball valve for maximum flow. Quarter-turn operation for quick and reliable shutoff.',
    specs:'1/2" NPT | 600 WOG | Lead-free brass | -20°F to 366°F | ANSI' },
  { id:12, name:'Ball Valve 3/4" Full Port Lead-Free', category:"Valves", price:24.99, unit:"each", sku:"BV-FP-075", inStock:true,
    desc:'Heavy-duty 3/4" full-port ball valve for main shutoffs and branch isolation. Locking handle available.',
    specs:'3/4" NPT | 600 WOG | Lead-free brass | Quarter-turn' },
  { id:13, name:'Pressure Reducing Valve 3/4"', category:"Valves", price:89.99, unit:"each", sku:"PRV-075", inStock:true,
    desc:'Adjustable pressure regulating valve. Factory set at 75 PSI. Protects fixtures and water heaters from pressure spikes.',
    specs:'3/4" NPT | 25–75 PSI adjustable | Lead-free | ASSE 1003' },
  { id:14, name:'Check Valve 1/2" Swing Type', category:"Valves", price:22.99, unit:"each", sku:"CV-SW-050", inStock:true,
    desc:'Swing check valve prevents backflow in water supply and pump discharge lines.',
    specs:'1/2" NPT | 200 WOG | Brass body | Stainless disc | Horizontal/vertical' },
  { id:15, name:'Thermostatic Mixing Valve 3/4"', category:"Valves", price:129.99, unit:"each", sku:"TMV-075", inStock:false,
    desc:'Blends hot and cold water to a safe preset temperature. Prevents scalding in residential and commercial applications.',
    specs:'3/4" NPT | 85–120°F adjustable | ASSE 1017 | Lead-free' },

  // WATER HEATERS
  { id:16, name:'Rheem Performance 40-Gal Gas Water Heater', category:"Water Heaters", price:649.99, unit:"each", sku:"RH-GAS-40", inStock:true,
    desc:'Natural gas residential water heater with 36,000 BTU burner. Powered anode rod for longer tank life. 6-year warranty.',
    specs:'40 gal | 36,000 BTU | 0.60 EF | FHR 72 gal | 6-yr tank warranty' },
  { id:17, name:'Rinnai RU199eN Tankless Water Heater', category:"Water Heaters", price:1249.99, unit:"each", sku:"RI-TL-199", inStock:true,
    desc:'Condensing ultra-efficient tankless gas water heater with endless hot water on demand. UltraHeat technology for cold climates.',
    specs:'9.8 GPM | 0.96 UEF | Natural gas | Indoor/outdoor | 12-yr heat exchanger' },
  { id:18, name:'Bradford White 50-Gal Electric Water Heater', category:"Water Heaters", price:589.99, unit:"each", sku:"BW-EL-50", inStock:true,
    desc:'Residential electric water heater with dual 4,500W elements. Vitraglas lining for long tank life.',
    specs:'50 gal | 240V | 4,500W elements | 0.92 EF | 6-yr warranty' },

  // FIXTURES
  { id:19, name:'Moen Chateau Kitchen Faucet Chrome', category:"Fixtures", price:189.99, unit:"each", sku:"MN-KF-CHA", inStock:true,
    desc:'Single-handle kitchen faucet with pull-out spray. Microban antimicrobial protection on handle. Moen Lifetime Warranty.',
    specs:'1-hole | 1.8 GPM | Pull-out spray | Chrome | Lifetime warranty' },
  { id:20, name:'Delta Monitor 14 Shower Valve Kit', category:"Fixtures", price:449.99, unit:"each", sku:"DL-SH-M14", inStock:true,
    desc:'Pressure-balanced shower valve with Monitor technology to prevent scalding from sudden pressure changes. Trim sold separately.',
    specs:'Monitor 14 | Rough-in valve + trim | ASSE 1016 | 0.5–8 GPM' },
  { id:21, name:'Kohler Cimarron Toilet Complete', category:"Fixtures", price:289.99, unit:"each", sku:"KH-TOI-CIM", inStock:true,
    desc:'AquaPiston flushing technology. Elongated bowl, comfort height, white. WaterSense certified at 1.28 GPF.',
    specs:'1.28 GPF | Elongated | 17" height | 12" rough-in | WaterSense' },
  { id:22, name:'Kohler Undertone Undermount Sink 33"', category:"Fixtures", price:249.99, unit:"each", sku:"KH-SNK-UT33", inStock:true,
    desc:'Single-basin stainless steel undermount kitchen sink. Sound-deadening pads included. Rack and drain basket included.',
    specs:'33"×22" | 18-gauge stainless | Undermount | Includes rack + grid' },

  // DRAINAGE
  { id:23, name:'P-Trap 1-1/2" Chrome Adjustable', category:"Drainage", price:12.99, unit:"each", sku:"PT-CHR-150", inStock:true,
    desc:'Adjustable P-trap for bathroom and kitchen sinks. Prevents sewer gas from entering. Chrome-plated ABS construction.',
    specs:'1-1/2" | Chrome-plated ABS | Slip-joint | Adjustable outlet' },
  { id:24, name:'Zoeller M53 Sump Pump 1/3 HP', category:"Drainage", price:199.99, unit:"each", sku:"ZO-SP-M53", inStock:true,
    desc:'Heavy-duty submersible sump pump with cast-iron base. Handles solids up to 1/2". Automatic float switch.',
    specs:'1/3 HP | 115V | 43 GPM | 1-1/2" discharge | Cast iron base' },
  { id:25, name:'InSinkErator Evolution 3/4 HP Disposal', category:"Drainage", price:159.99, unit:"each", sku:"ISE-GD-075", inStock:true,
    desc:'Continuous-feed garbage disposal with stainless steel grind components and sound insulation shell.',
    specs:'3/4 HP | 1,725 RPM | Stainless components | 5-yr in-home warranty' },
  { id:26, name:'Floor Drain 4" Round Stainless', category:"Drainage", price:29.99, unit:"each", sku:"FD-SS-400", inStock:true,
    desc:'Round floor drain with adjustable strainer. Suitable for garage, basement, and utility room installations.',
    specs:'4" round | Stainless strainer | Cast-iron body | Bottom outlet | ADA' },

  // TOOLS
  { id:27, name:'Ridgid Pipe Cutter 1/8"–1-1/8"', category:"Tools", price:24.99, unit:"each", sku:"TL-PC-RDG", inStock:true,
    desc:'Ratchet-type pipe cutter for copper, aluminum, and thin-wall conduit. Clean cuts without deburring needed.',
    specs:'1/8"–1-1/8" capacity | Ratchet action | Replaceable wheel | Chrome-moly' },
  { id:28, name:'Teflon Thread Seal Tape (3-Pack)', category:"Tools", price:5.99, unit:"pack", sku:"TL-PTFE-3PK", inStock:true,
    desc:'Pink thread seal tape rated for gas lines and NPT fittings. Prevents leaks at all threaded connections.',
    specs:'1/2" wide | 3 rolls | PTFE | Gas-rated | 520" per roll' },
  { id:29, name:'Oatey PVC Cement & Primer Kit', category:"Tools", price:14.99, unit:"kit", sku:"TL-PVC-KIT", inStock:true,
    desc:'All-in-one PVC cement and primer for Schedule 40 and 80 pipe. NSF-61 certified for potable water.',
    specs:'8oz cement + 4oz primer | Schedule 40 & 80 | NSF-14/61 | Low-VOC' },
  { id:30, name:'Oatey Pipe Thread Compound 1 lb', category:"Tools", price:8.99, unit:"jar", sku:"TL-PTC-1LB", inStock:true,
    desc:'Non-hardening pipe thread compound for all metals and plastic. Prevents rust, corrosion, and leaks.',
    specs:'1 lb jar | Non-hardening | All metals & plastic | NSF-61' },

  // FILTRATION
  { id:31, name:'3M Whole House Water Filter 3-Stage', category:"Filtration", price:199.99, unit:"each", sku:"FI-WH-3STG", inStock:true,
    desc:'3-stage whole house filtration with sediment, carbon block, and post-carbon filters. 100,000-gallon capacity.',
    specs:'3/4" ports | 100K-gal capacity | 15 GPM | 7"×20" filters | Scale inhibitor' },
  { id:32, name:'iSpring RCC7AK 6-Stage RO System', category:"Filtration", price:259.99, unit:"each", sku:"FI-RO-6ST", inStock:true,
    desc:'Under-sink reverse osmosis with alkaline remineralization stage. 75 GPD. NSF-58 certified.',
    specs:'6 stages | 75 GPD | Alkaline filter | 3:1 pure-to-drain ratio | NSF-58' },
  { id:33, name:'Fleck 5600SXT Water Softener 48K Grain', category:"Filtration", price:699.99, unit:"each", sku:"FI-WS-48K", inStock:true,
    desc:'Digital metered water softener with Fleck 5600SXT valve. Demand-initiated regeneration saves salt and water.',
    specs:'48,000 grain | Digital metered | 12 GPM service | 1" bypass included' },
];

const CATEGORIES = ["All","Pipes","Fittings","Valves","Water Heaters","Fixtures","Drainage","Tools","Filtration"];

const TEST_QUESTIONS = [
  { q:"What PEX pipe sizes do you carry and what are the prices?", topic:"Products" },
  { q:"What's the difference between PEX and copper pipe? Which should I choose?", topic:"Knowledge" },
  { q:"Can you recommend a water heater for a family of 4 with a busy morning schedule?", topic:"Recommendation" },
  { q:"What valve should I use for a main water shutoff?", topic:"Recommendation" },
  { q:"Do you have SharkBite push-to-connect fittings?", topic:"Products" },
  { q:"What's the price and model of your sump pump?", topic:"Pricing" },
  { q:"How do I prevent backflow in a pump discharge line?", topic:"Technical" },
  { q:"What's the GPF rating on your toilet and is it WaterSense certified?", topic:"Specs" },
  { q:"I need to filter my whole house water. What options do you have?", topic:"Recommendation" },
  { q:"What's your return policy and warranty terms?", topic:"Policies" },
];

// ─── MAIN APP ────────────────────────────────────────────────────────────────
export default function App() {
  const [activeTab, setActiveTab] = useState("chat");
  const [products, setProducts] = useState(INITIAL_PRODUCTS);
  const [messages, setMessages] = useState([
    { role:"assistant", content:"Hi! I'm your AI plumbing sales assistant at ProPlumb Supply.\n\nI know our full catalog of pipes, fittings, valves, water heaters, fixtures, tools, and filtration systems — and I can help you find exactly what you need.\n\nWhat project are you working on today?" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [catFilter, setCatFilter] = useState("All");
  const [search, setSearch] = useState("");
  const [companyInfo, setCompanyInfo] = useState({
    name:"ProPlumb Supply",
    tagline:"Quality Plumbing Products for Professionals & DIYers",
    returnPolicy:"30-day returns on unused, unopened items with receipt",
    warranty:"All products carry full manufacturer warranty",
    delivery:"Free delivery on orders over $500 within 25 miles",
    hours:"Mon–Fri 7am–6pm | Sat 8am–4pm | Sun Closed",
    phone:"(555) 748-2600",
    specialty:"Plumbing supplies, fixtures, water treatment, and tools"
  });
  const [customQA, setCustomQA] = useState([
    { q:"Do you offer installation services?", a:"We partner with licensed plumbers in the area. Ask at the counter for our contractor referral list." },
    { q:"Can I order products that are out of stock?", a:"Yes! We can special-order most items with a 3–5 business day lead time. Ask a sales rep for details." }
  ]);
  const [newQA, setNewQA] = useState({ q:"", a:"" });
  const [testResults, setTestResults] = useState([]);
  const [isTesting, setIsTesting] = useState(false);
  const [currentTestIdx, setCurrentTestIdx] = useState(-1);
  const [showAddProduct, setShowAddProduct] = useState(false);
  const [newProd, setNewProd] = useState({ name:"", category:"Pipes", price:"", sku:"", desc:"", specs:"", unit:"each" });
  const [editComp, setEditComp] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior:"smooth" });
  }, [messages, isLoading]);

  // Build system prompt from all training data
  const buildSystemPrompt = () => {
    const productList = products.map(p =>
      `• ${p.name} (SKU: ${p.sku || "N/A"}) | ${p.category} | $${p.price.toFixed(2)}/${p.unit} | ${p.inStock ? "✓ IN STOCK" : "✗ OUT OF STOCK"}\n  ${p.desc}\n  Specs: ${p.specs}`
    ).join("\n\n");

    const qaBlock = customQA.length > 0
      ? "\n\n── CUSTOM TRAINED Q&A ──\n" + customQA.map(qa => `Q: ${qa.q}\nA: ${qa.a}`).join("\n\n")
      : "";

    return `You are a highly knowledgeable AI sales assistant for ${companyInfo.name} — ${companyInfo.tagline}.

── BUSINESS INFO ──
Phone: ${companyInfo.phone}
Hours: ${companyInfo.hours}
Specialty: ${companyInfo.specialty}
Return Policy: ${companyInfo.returnPolicy}
Warranty: ${companyInfo.warranty}
Delivery: ${companyInfo.delivery}

── FULL PRODUCT CATALOG (${products.length} items) ──
${productList}
${qaBlock}

── YOUR ROLE ──
- Help customers find the right plumbing products for their specific project
- Provide accurate pricing and stock status directly from the catalog above
- Give confident technical advice (pipe sizing, valve selection, installation tips)
- Compare products clearly when a customer is deciding between options
- Always quote SKU numbers when recommending specific products
- If a product isn't in the catalog, say so honestly and suggest the closest alternative
- Keep responses helpful and concise — avoid walls of text
- Be warm, professional, and genuinely helpful like an expert plumbing counter person`;
  };

  // Send chat message
  const sendMessage = async (overrideInput) => {
    const text = (overrideInput ?? input).trim();
    if (!text || isLoading) return;
    const userMsg = { role:"user", content:text };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setIsLoading(true);
    try {
      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body: JSON.stringify({
          model:"claude-sonnet-4-6",
          max_tokens:1000,
          system: buildSystemPrompt(),
          messages: updated.map(m => ({ role:m.role, content:m.content }))
        })
      });
      const data = await res.json();
      const reply = data.content?.filter(b => b.type==="text").map(b => b.text).join("") || "I couldn't get a response. Please try again.";
      setMessages([...updated, { role:"assistant", content:reply }]);
    } catch {
      setMessages([...updated, { role:"assistant", content:"Connection error. Please check your network and try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Run full test suite
  const runTests = async () => {
    setIsTesting(true);
    setTestResults([]);
    const results = [];
    for (let i = 0; i < TEST_QUESTIONS.length; i++) {
      setCurrentTestIdx(i);
      const test = TEST_QUESTIONS[i];
      try {
        const res = await fetch("https://api.anthropic.com/v1/messages", {
          method:"POST",
          headers:{ "Content-Type":"application/json" },
          body: JSON.stringify({
            model:"claude-sonnet-4-6",
            max_tokens:600,
            system: buildSystemPrompt(),
            messages:[{ role:"user", content:test.q }]
          })
        });
        const data = await res.json();
        const answer = data.content?.filter(b => b.type==="text").map(b => b.text).join("") || "No response";
        results.push({ ...test, answer, status:"pass" });
      } catch {
        results.push({ ...test, answer:"API error — test could not complete.", status:"fail" });
      }
      setTestResults([...results]);
    }
    setCurrentTestIdx(-1);
    setIsTesting(false);
  };

  const addProduct = () => {
    if (!newProd.name.trim() || !newProd.price) return;
    setProducts([...products, { ...newProd, id:Date.now(), price:parseFloat(newProd.price), inStock:true }]);
    setNewProd({ name:"", category:"Pipes", price:"", sku:"", desc:"", specs:"", unit:"each" });
    setShowAddProduct(false);
  };

  const addQA = () => {
    if (!newQA.q.trim() || !newQA.a.trim()) return;
    setCustomQA([...customQA, { ...newQA }]);
    setNewQA({ q:"", a:"" });
  };

  const filtered = products.filter(p => {
    const mc = catFilter === "All" || p.category === catFilter;
    const ms = !search || p.name.toLowerCase().includes(search.toLowerCase()) || p.desc.toLowerCase().includes(search.toLowerCase()) || p.category.toLowerCase().includes(search.toLowerCase());
    return mc && ms;
  });

  // ── STYLES ─────────────────────────────────────────────────────────────────
  const S = {
    card: { background:"var(--color-background-primary)", border:"0.5px solid var(--color-border-tertiary)", borderRadius:"var(--border-radius-lg)", padding:"1rem 1.25rem" },
    pill: (on) => ({ padding:"5px 12px", borderRadius:20, border: on ? "2px solid var(--color-border-info)" : "0.5px solid var(--color-border-tertiary)", background: on ? "var(--color-background-info)" : "var(--color-background-secondary)", color: on ? "var(--color-text-info)" : "var(--color-text-secondary)", cursor:"pointer", fontSize:12, fontWeight: on ? 500 : 400, whiteSpace:"nowrap" }),
    tab: (on) => ({ padding:"10px 18px", borderBottom: on ? "2px solid var(--color-text-info)" : "2px solid transparent", background:"none", border:"none", borderBottom: on ? "2px solid var(--color-text-info)" : "2px solid transparent", color: on ? "var(--color-text-info)" : "var(--color-text-secondary)", cursor:"pointer", fontSize:14, fontWeight: on ? 500 : 400, display:"flex", alignItems:"center", gap:6 }),
    badge: (type) => {
      const map = { success:["var(--color-background-success)","var(--color-text-success)"], danger:["var(--color-background-danger)","var(--color-text-danger)"], info:["var(--color-background-info)","var(--color-text-info)"], neutral:["var(--color-background-secondary)","var(--color-text-secondary)"] };
      const [bg, fg] = map[type] || map.neutral;
      return { padding:"2px 8px", borderRadius:10, background:bg, color:fg, fontSize:11, fontWeight:500, whiteSpace:"nowrap" };
    },
    input: { fontSize:13, width:"100%", boxSizing:"border-box" },
    btn: { fontSize:13, padding:"8px 14px", display:"flex", alignItems:"center", gap:6 },
    label: { display:"block", fontSize:11, color:"var(--color-text-secondary)", marginBottom:4 }
  };

  const QUICK_ASKS = [
    "Help me choose a water heater for a family of 4",
    "What's the best valve for a main shutoff?",
    "PEX vs copper — which should I use?",
    "What filtration system do you recommend?",
    "Do you have SharkBite fittings in stock?"
  ];

  return (
    <div style={{ fontFamily:"var(--font-sans)", maxWidth:900, margin:"0 auto", paddingBottom:"2rem" }}>
      <h2 className="sr-only">ProPlumb AI Sales Assistant — Plumbing Products Catalog and Chat</h2>

      {/* ── HEADER ── */}
      <div style={{ borderBottom:"0.5px solid var(--color-border-tertiary)", paddingBottom:0, marginBottom:0 }}>
        <div style={{ display:"flex", alignItems:"center", gap:12, padding:"1rem 0 12px" }}>
          <div style={{ width:40, height:40, borderRadius:10, background:"var(--color-background-info)", display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0 }}>
            <i className="ti ti-droplet-filled" style={{ fontSize:22, color:"var(--color-text-info)" }} aria-hidden="true" />
          </div>
          <div>
            <h2 style={{ margin:0, fontSize:17, fontWeight:500 }}>ProPlumb AI Sales Assistant</h2>
            <p style={{ margin:0, fontSize:12, color:"var(--color-text-secondary)" }}>AI Products for Plumbers · {products.length} products loaded</p>
          </div>
          <div style={{ marginLeft:"auto", display:"flex", gap:6, flexShrink:0 }}>
            <span style={S.badge("success")}><i className="ti ti-check" style={{ fontSize:11 }} /> {products.filter(p=>p.inStock).length} in stock</span>
            <span style={S.badge("info")}><i className="ti ti-brain" style={{ fontSize:11 }} /> AI trained</span>
          </div>
        </div>

        {/* Tab bar */}
        <div style={{ display:"flex", gap:0, borderBottom:"0.5px solid var(--color-border-tertiary)" }}>
          {[["chat","ti-message-2","Sales Chat"],["products","ti-package","Products"],["train","ti-brain","Train AI"],["test","ti-test-pipe","Test Suite"]].map(([id,icon,label]) => (
            <button key={id} onClick={() => setActiveTab(id)} style={S.tab(activeTab===id)}>
              <i className={`ti ${icon}`} style={{ fontSize:15 }} aria-hidden="true" />{label}
            </button>
          ))}
        </div>
      </div>

      {/* ══ SALES CHAT TAB ══════════════════════════════════════════════════════ */}
      {activeTab === "chat" && (
        <div style={{ display:"flex", flexDirection:"column" }}>
          {/* Messages */}
          <div style={{ minHeight:420, maxHeight:480, overflowY:"auto", paddingTop:"1rem", display:"flex", flexDirection:"column", gap:10 }}>
            {messages.map((m, i) => (
              <div key={i} style={{ display:"flex", justifyContent: m.role==="user" ? "flex-end" : "flex-start" }}>
                {m.role === "assistant" && (
                  <div style={{ width:28, height:28, borderRadius:"50%", background:"var(--color-background-info)", display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0, marginRight:8, marginTop:2 }}>
                    <i className="ti ti-robot" style={{ fontSize:14, color:"var(--color-text-info)" }} aria-hidden="true" />
                  </div>
                )}
                <div style={{
                  maxWidth:"72%", padding:"10px 14px",
                  borderRadius: m.role==="user" ? "16px 4px 16px 16px" : "4px 16px 16px 16px",
                  background: m.role==="user" ? "var(--color-background-info)" : "var(--color-background-secondary)",
                  color: m.role==="user" ? "var(--color-text-info)" : "var(--color-text-primary)",
                  fontSize:14, lineHeight:1.65, whiteSpace:"pre-wrap"
                }}>
                  {m.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                <div style={{ width:28, height:28, borderRadius:"50%", background:"var(--color-background-info)", display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0 }}>
                  <i className="ti ti-robot" style={{ fontSize:14, color:"var(--color-text-info)" }} aria-hidden="true" />
                </div>
                <div style={{ padding:"10px 14px", borderRadius:"4px 16px 16px 16px", background:"var(--color-background-secondary)", fontSize:14, color:"var(--color-text-tertiary)" }}>
                  Thinking…
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick questions */}
          <div style={{ display:"flex", gap:6, flexWrap:"wrap", padding:"10px 0 8px", borderTop:"0.5px solid var(--color-border-tertiary)" }}>
            {QUICK_ASKS.map(q => (
              <button key={q} onClick={() => sendMessage(q)} disabled={isLoading} style={{ ...S.pill(false), fontSize:12 }}>{q}</button>
            ))}
          </div>

          {/* Input row */}
          <div style={{ display:"flex", gap:8 }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key==="Enter" && !e.shiftKey && sendMessage()}
              placeholder="Ask about products, pricing, sizing, installation…"
              style={{ flex:1, fontSize:14 }}
              disabled={isLoading}
            />
            <button onClick={() => sendMessage()} disabled={isLoading || !input.trim()} style={{ padding:"0 18px", display:"flex", alignItems:"center", gap:6 }}>
              <i className="ti ti-send" style={{ fontSize:15 }} aria-hidden="true" /> Send
            </button>
          </div>
          <p style={{ margin:"6px 0 0", fontSize:11, color:"var(--color-text-tertiary)" }}>
            Trained on {products.length} products · {customQA.length} custom Q&A pairs · Press Enter to send
          </p>
        </div>
      )}

      {/* ══ PRODUCTS TAB ════════════════════════════════════════════════════════ */}
      {activeTab === "products" && (
        <div style={{ paddingTop:"1rem" }}>
          {/* Search + Add */}
          <div style={{ display:"flex", gap:8, marginBottom:12 }}>
            <div style={{ position:"relative", flex:1 }}>
              <i className="ti ti-search" style={{ position:"absolute", left:10, top:"50%", transform:"translateY(-50%)", fontSize:15, color:"var(--color-text-tertiary)" }} aria-hidden="true" />
              <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search products by name, category, or description…" style={{ width:"100%", paddingLeft:34, fontSize:13, boxSizing:"border-box" }} />
            </div>
            <button onClick={() => setShowAddProduct(!showAddProduct)} style={S.btn}>
              <i className="ti ti-plus" aria-hidden="true" /> Add product
            </button>
          </div>

          {/* Category filters */}
          <div style={{ display:"flex", gap:6, flexWrap:"wrap", marginBottom:14 }}>
            {CATEGORIES.map(c => (
              <button key={c} onClick={() => setCatFilter(c)} style={S.pill(catFilter===c)}>{c}</button>
            ))}
          </div>

          {/* Add product form */}
          {showAddProduct && (
            <div style={{ ...S.card, marginBottom:16, borderColor:"var(--color-border-info)" }}>
              <h3 style={{ margin:"0 0 12px", fontSize:15, fontWeight:500 }}><i className="ti ti-plus" aria-hidden="true" /> Add new product to catalog</h3>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:8, marginBottom:8 }}>
                <div style={{ gridColumn:"1/-1" }}>
                  <label style={S.label}>Product name *</label>
                  <input value={newProd.name} onChange={e => setNewProd({...newProd, name:e.target.value})} placeholder="e.g. Copper Pipe Type M 3/4 × 10ft" style={S.input} />
                </div>
                <div>
                  <label style={S.label}>Category *</label>
                  <select value={newProd.category} onChange={e => setNewProd({...newProd, category:e.target.value})} style={{ ...S.input, height:36 }}>
                    {CATEGORIES.filter(c=>c!=="All").map(c => <option key={c}>{c}</option>)}
                  </select>
                </div>
                <div>
                  <label style={S.label}>Price ($) *</label>
                  <input type="number" min="0" step="0.01" value={newProd.price} onChange={e => setNewProd({...newProd, price:e.target.value})} placeholder="0.00" style={S.input} />
                </div>
                <div>
                  <label style={S.label}>Unit</label>
                  <input value={newProd.unit} onChange={e => setNewProd({...newProd, unit:e.target.value})} placeholder="each / roll / kit" style={S.input} />
                </div>
                <div>
                  <label style={S.label}>SKU</label>
                  <input value={newProd.sku} onChange={e => setNewProd({...newProd, sku:e.target.value})} placeholder="e.g. COP-M-075-10" style={S.input} />
                </div>
                <div style={{ gridColumn:"1/-1" }}>
                  <label style={S.label}>Description</label>
                  <textarea value={newProd.desc} onChange={e => setNewProd({...newProd, desc:e.target.value})} placeholder="Product description…" style={{ ...S.input, minHeight:56, resize:"vertical" }} />
                </div>
                <div style={{ gridColumn:"1/-1" }}>
                  <label style={S.label}>Specifications</label>
                  <input value={newProd.specs} onChange={e => setNewProd({...newProd, specs:e.target.value})} placeholder="e.g. 3/4 dia | Type M | 10ft | Lead-free" style={S.input} />
                </div>
              </div>
              <div style={{ display:"flex", gap:8 }}>
                <button onClick={addProduct} style={S.btn}><i className="ti ti-check" aria-hidden="true" /> Add to catalog</button>
                <button onClick={() => setShowAddProduct(false)} style={S.btn}><i className="ti ti-x" aria-hidden="true" /> Cancel</button>
              </div>
            </div>
          )}

          {/* Product count */}
          <p style={{ margin:"0 0 12px", fontSize:12, color:"var(--color-text-secondary)" }}>
            Showing {filtered.length} of {products.length} products
          </p>

          {/* Product grid */}
          <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill, minmax(250px, 1fr))", gap:12 }}>
            {filtered.map(p => (
              <div key={p.id} style={{ ...S.card }}>
                <div style={{ display:"flex", justifyContent:"space-between", marginBottom:8 }}>
                  <span style={S.badge("neutral")}>{p.category}</span>
                  <span style={S.badge(p.inStock ? "success" : "danger")}>{p.inStock ? "In stock" : "Out of stock"}</span>
                </div>
                <p style={{ margin:"0 0 4px", fontSize:13, fontWeight:500, lineHeight:1.35 }}>{p.name}</p>
                <p style={{ margin:"0 0 8px", fontSize:19, fontWeight:500, color:"var(--color-text-info)" }}>
                  ${p.price.toFixed(2)}
                  <span style={{ fontSize:11, fontWeight:400, color:"var(--color-text-secondary)" }}> /{p.unit}</span>
                </p>
                <p style={{ margin:"0 0 6px", fontSize:12, color:"var(--color-text-secondary)", lineHeight:1.55 }}>{p.desc}</p>
                <p style={{ margin:"0 0 4px", fontSize:11, color:"var(--color-text-tertiary)", fontFamily:"var(--font-mono)", lineHeight:1.5 }}>{p.specs}</p>
                {p.sku && <p style={{ margin:0, fontSize:11, color:"var(--color-text-tertiary)" }}>SKU: {p.sku}</p>}
              </div>
            ))}
          </div>

          {filtered.length === 0 && (
            <div style={{ textAlign:"center", padding:"3rem 0", color:"var(--color-text-secondary)" }}>
              <i className="ti ti-search-off" style={{ fontSize:32, display:"block", marginBottom:8 }} aria-hidden="true" />
              <p style={{ margin:0 }}>No products match your search. Try a different term or category.</p>
            </div>
          )}
        </div>
      )}

      {/* ══ TRAIN AI TAB ════════════════════════════════════════════════════════ */}
      {activeTab === "train" && (
        <div style={{ paddingTop:"1rem", display:"flex", flexDirection:"column", gap:14 }}>
          {/* Status banner */}
          <div style={{ padding:"12px 16px", borderRadius:"var(--border-radius-md)", background:"var(--color-background-success)", border:"0.5px solid var(--color-border-success)", display:"flex", alignItems:"center", gap:10 }}>
            <i className="ti ti-check" style={{ fontSize:18, color:"var(--color-text-success)", flexShrink:0 }} aria-hidden="true" />
            <div>
              <p style={{ margin:0, fontSize:13, fontWeight:500, color:"var(--color-text-success)" }}>AI training active</p>
              <p style={{ margin:0, fontSize:12, color:"var(--color-text-success)" }}>
                Trained on {products.length} catalog products, {customQA.length} custom Q&A pairs, and your company info. Changes apply instantly.
              </p>
            </div>
          </div>

          {/* Company info */}
          <div style={S.card}>
            <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:12 }}>
              <h3 style={{ margin:0, fontSize:15, fontWeight:500, display:"flex", alignItems:"center", gap:8 }}>
                <i className="ti ti-building-store" aria-hidden="true" /> Company information
              </h3>
              <button onClick={() => setEditComp(!editComp)} style={{ ...S.btn, fontSize:12 }}>
                <i className={`ti ti-${editComp ? "check" : "edit"}`} aria-hidden="true" /> {editComp ? "Done" : "Edit"}
              </button>
            </div>
            {editComp ? (
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:8 }}>
                {[["name","Company name"],["tagline","Tagline"],["phone","Phone number"],["hours","Business hours"],["returnPolicy","Return policy"],["warranty","Warranty info"],["delivery","Delivery policy"],["specialty","Specialty / focus"]].map(([key,label]) => (
                  <div key={key} style={{ gridColumn: ["tagline","returnPolicy","warranty","delivery","specialty"].includes(key) ? "1/-1" : "auto" }}>
                    <label style={S.label}>{label}</label>
                    <input value={companyInfo[key]} onChange={e => setCompanyInfo({...companyInfo, [key]:e.target.value})} style={S.input} />
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:6 }}>
                {Object.entries(companyInfo).map(([key, val]) => (
                  <div key={key} style={{ borderBottom:"0.5px solid var(--color-border-tertiary)", padding:"6px 0" }}>
                    <p style={{ margin:0, fontSize:11, color:"var(--color-text-secondary)", textTransform:"capitalize" }}>{key.replace(/([A-Z])/g," $1").trim()}</p>
                    <p style={{ margin:0, fontSize:13 }}>{val}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Custom Q&A */}
          <div style={S.card}>
            <h3 style={{ margin:"0 0 6px", fontSize:15, fontWeight:500, display:"flex", alignItems:"center", gap:8 }}>
              <i className="ti ti-messages" aria-hidden="true" /> Custom Q&A training
              <span style={{ fontSize:12, fontWeight:400, color:"var(--color-text-secondary)" }}>({customQA.length} pairs)</span>
            </h3>
            <p style={{ margin:"0 0 14px", fontSize:13, color:"var(--color-text-secondary)" }}>
              Add custom question-and-answer pairs to teach the AI about your specific policies, talking points, or frequently asked questions.
            </p>
            <div style={{ display:"flex", flexDirection:"column", gap:8, marginBottom:14, padding:"12px 14px", borderRadius:"var(--border-radius-md)", background:"var(--color-background-secondary)" }}>
              <div>
                <label style={S.label}>Question *</label>
                <input value={newQA.q} onChange={e => setNewQA({...newQA, q:e.target.value})} placeholder="e.g. Do you offer commercial accounts?" style={S.input} />
              </div>
              <div>
                <label style={S.label}>Answer *</label>
                <textarea value={newQA.a} onChange={e => setNewQA({...newQA, a:e.target.value})} placeholder="e.g. Yes! We offer net-30 commercial accounts for licensed plumbing contractors." style={{ ...S.input, minHeight:64, resize:"vertical" }} />
              </div>
              <button onClick={addQA} style={{ ...S.btn, alignSelf:"flex-start" }}>
                <i className="ti ti-plus" aria-hidden="true" /> Add Q&A pair
              </button>
            </div>

            {/* Existing Q&A pairs */}
            {customQA.length === 0 && (
              <p style={{ fontSize:13, color:"var(--color-text-tertiary)", textAlign:"center", padding:"1rem 0" }}>No custom Q&A pairs yet. Add your first one above.</p>
            )}
            <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
              {customQA.map((qa, i) => (
                <div key={i} style={{ padding:"10px 12px", borderRadius:"var(--border-radius-md)", border:"0.5px solid var(--color-border-tertiary)", background:"var(--color-background-primary)" }}>
                  <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start" }}>
                    <div style={{ flex:1 }}>
                      <p style={{ margin:"0 0 4px", fontSize:13, fontWeight:500, color:"var(--color-text-info)" }}>Q: {qa.q}</p>
                      <p style={{ margin:0, fontSize:13, color:"var(--color-text-secondary)", lineHeight:1.5 }}>A: {qa.a}</p>
                    </div>
                    <button onClick={() => setCustomQA(customQA.filter((_,j) => j!==i))} style={{ ...S.btn, padding:"4px 8px", marginLeft:10, flexShrink:0 }}>
                      <i className="ti ti-trash" style={{ fontSize:13 }} aria-hidden="true" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Catalog training note */}
          <div style={{ ...S.card, background:"var(--color-background-secondary)", border:"none" }}>
            <h3 style={{ margin:"0 0 8px", fontSize:14, fontWeight:500, display:"flex", alignItems:"center", gap:8 }}>
              <i className="ti ti-package" aria-hidden="true" /> Product catalog training
            </h3>
            <p style={{ margin:"0 0 8px", fontSize:13, color:"var(--color-text-secondary)" }}>
              The AI automatically knows every product in your catalog — name, price, specs, availability, and SKU. Add or edit products in the Products tab, and the AI learns instantly.
            </p>
            <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
              {CATEGORIES.filter(c=>c!=="All").map(c => {
                const count = products.filter(p=>p.category===c).length;
                return count > 0 ? <span key={c} style={S.badge("neutral")}>{c}: {count}</span> : null;
              })}
            </div>
          </div>
        </div>
      )}

      {/* ══ TEST SUITE TAB ══════════════════════════════════════════════════════ */}
      {activeTab === "test" && (
        <div style={{ paddingTop:"1rem" }}>
          {/* Header row */}
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:16 }}>
            <div>
              <h3 style={{ margin:"0 0 4px", fontSize:15, fontWeight:500 }}>AI assistant test suite</h3>
              <p style={{ margin:0, fontSize:13, color:"var(--color-text-secondary)" }}>
                Automatically tests the AI on {TEST_QUESTIONS.length} real sales questions to verify it knows your products and policies.
              </p>
            </div>
            <button onClick={runTests} disabled={isTesting} style={{ ...S.btn, flexShrink:0 }}>
              {isTesting
                ? <><i className="ti ti-loader" style={{ fontSize:14 }} aria-hidden="true" /> Running…</>
                : <><i className="ti ti-player-play" style={{ fontSize:14 }} aria-hidden="true" /> Run all tests</>
              }
            </button>
          </div>

          {/* Score summary */}
          {testResults.length > 0 && (
            <div style={{ display:"grid", gridTemplateColumns:"repeat(4, 1fr)", gap:10, marginBottom:16 }}>
              {[
                ["Tests run", testResults.length, "ti-list-check", "neutral"],
                ["Passed", testResults.filter(r=>r.status==="pass").length, "ti-check", "success"],
                ["Failed", testResults.filter(r=>r.status==="fail").length, "ti-x", "danger"],
                ["Pass rate", Math.round(testResults.filter(r=>r.status==="pass").length/testResults.length*100)+"%", "ti-chart-bar", "info"]
              ].map(([label, val, icon, type]) => (
                <div key={label} style={{ padding:"1rem", background:"var(--color-background-secondary)", borderRadius:"var(--border-radius-md)", textAlign:"center" }}>
                  <i className={`ti ${icon}`} style={{ fontSize:20, color:`var(--color-text-${type})` }} aria-hidden="true" />
                  <p style={{ margin:"6px 0 2px", fontSize:22, fontWeight:500 }}>{val}</p>
                  <p style={{ margin:0, fontSize:12, color:"var(--color-text-secondary)" }}>{label}</p>
                </div>
              ))}
            </div>
          )}

          {/* Empty state */}
          {testResults.length === 0 && !isTesting && (
            <div style={{ ...S.card, textAlign:"center", padding:"2.5rem 1rem", marginBottom:16 }}>
              <i className="ti ti-test-pipe" style={{ fontSize:36, color:"var(--color-text-tertiary)", display:"block", marginBottom:8 }} aria-hidden="true" />
              <p style={{ margin:"0 0 4px", fontSize:14, fontWeight:500 }}>No tests run yet</p>
              <p style={{ margin:0, fontSize:13, color:"var(--color-text-secondary)" }}>
                Click "Run all tests" to evaluate the AI on {TEST_QUESTIONS.length} standardized plumbing sales questions.
              </p>
            </div>
          )}

          {/* Test question cards */}
          <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
            {TEST_QUESTIONS.map((test, i) => {
              const result = testResults[i];
              const isRunning = isTesting && i === currentTestIdx;
              const isPending = i >= testResults.length && !isRunning;
              return (
                <div key={i} style={{ ...S.card }}>
                  <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", gap:12, marginBottom:6 }}>
                    <div style={{ flex:1 }}>
                      <p style={{ margin:"0 0 6px", fontSize:13, fontWeight:500 }}>
                        <span style={{ color:"var(--color-text-tertiary)", marginRight:6 }}>#{i+1}</span>
                        {test.q}
                      </p>
                      <span style={S.badge("neutral")}>{test.topic}</span>
                    </div>
                    <span style={S.badge(isRunning ? "info" : result ? (result.status==="pass" ? "success" : "danger") : "neutral")}>
                      {isRunning ? "Running…" : result ? (result.status==="pass" ? "✓ Pass" : "✗ Fail") : "Pending"}
                    </span>
                  </div>
                  {isRunning && (
                    <div style={{ marginTop:8, padding:"8px 10px", borderRadius:"var(--border-radius-md)", background:"var(--color-background-secondary)", fontSize:12, color:"var(--color-text-secondary)" }}>
                      <i className="ti ti-dots" aria-hidden="true" /> AI is answering this question…
                    </div>
                  )}
                  {result && (
                    <div style={{ marginTop:8, padding:"10px 12px", borderRadius:"var(--border-radius-md)", background:"var(--color-background-secondary)", fontSize:12, color:"var(--color-text-secondary)", lineHeight:1.65, maxHeight:140, overflowY:"auto", whiteSpace:"pre-wrap" }}>
                      {result.answer}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {isTesting && (
            <p style={{ margin:"12px 0 0", fontSize:12, color:"var(--color-text-secondary)", textAlign:"center" }}>
              Running test {Math.min(currentTestIdx+1, TEST_QUESTIONS.length)} of {TEST_QUESTIONS.length}…
            </p>
          )}
        </div>
      )}
    </div>
  );
}
