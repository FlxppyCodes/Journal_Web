import { useEffect, useMemo, useState } from "react";
import "./index.css";

const API = "/api";

const habits = [
  ["gym", "🏋️", "Gym"],
  ["breathing", "🫁", "Breathing"],
  ["coding", "💻", "Coding"],
  ["electronics", "🔧", "Electronics"],
  ["socializing", "🫂", "Socializing"],
  ["piano", "🎹", "Piano"],
  ["guitar", "🎸", "Guitar"],
  ["content", "🎥", "Content"],
  ["agency", "💼", "Agency"],
  ["manifestation", "✨", "Manifesting"],
  ["assignments", "📚", "Assignments"],
  ["youth", "🌍", "Youth Exchange"],
];

const moods = [
  ["😀", "Great"],
  ["🙂", "Good"],
  ["😐", "Okay"],
  ["🙁", "Low"],
  ["😮", "Surprised"],
];

const wellness = [
  ["❤️", "Happiness"],
  ["💪", "Physical"],
  ["🧠", "Mental"],
  ["⚡", "Productivity"],
  ["🌿", "Me-time"],
];

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function monthISO() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-01`;
}

async function api(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }

  const type = response.headers.get("content-type") || "";
  return type.includes("application/json") ? response.json() : null;
}

function Card({ children, className = "" }) {
  return <div className={`card ${className}`}>{children}</div>;
}

function SectionTitle({ eyebrow, title, action }) {
  return (
    <div className="section-title">
      <div>
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
        <h2>{title}</h2>
      </div>
      {action}
    </div>
  );
}

function ProgressRing({ value, total }) {
  const percent = total ? Math.round((value / total) * 100) : 0;

  return (
    <div
      className="progress-ring"
      style={{ "--progress": `${percent * 3.6}deg` }}
    >
      <div>
        <strong>{value}</strong>
        <span>/{total}</span>
      </div>
    </div>
  );
}

function Today({ data, setData, notify }) {
  const completed = Object.values(data.habits).filter(Boolean).length;

  async function saveMood(mood) {
    setData((d) => ({ ...d, mood }));
    try {
      await api("/mood", {
        method: "POST",
        body: JSON.stringify({
          entry_date: todayISO(),
          mood,
        }),
      });
      notify("Mood saved ✨");
    } catch {
      notify("Saved locally — API needs its exact field format");
    }
  }

  async function saveWellness(name, value) {
    const next = { ...data.wellness, [name]: value };
    setData((d) => ({ ...d, wellness: next }));

    try {
      await api("/wellness", {
        method: "POST",
        body: JSON.stringify({
          entry_date: todayISO(),
          category: name,
          rating: value,
        }),
      });
      notify("Wellness saved");
    } catch {
      notify("Saved locally");
    }
  }

  async function saveSleep(value) {
    setData((d) => ({ ...d, sleep: value }));

    try {
      await api("/sleep", {
        method: "POST",
        body: JSON.stringify({
          entry_date: todayISO(),
          hours: value,
        }),
      });
      notify("Sleep saved 🌙");
    } catch {
      notify("Saved locally");
    }
  }

  async function toggleHabit(id) {
    const next = !data.habits[id];
    setData((d) => ({
      ...d,
      habits: { ...d.habits, [id]: next },
    }));

    try {
      await api("/habit", {
        method: "POST",
        body: JSON.stringify({
          entry_date: todayISO(),
          habit: id,
          completed: next,
        }),
      });
    } catch {
      notify("Habit saved locally");
    }
  }

  async function submitToday() {
    const completed = habits
      .filter(([id]) => data.habits?.[id])
      .map(([, , name]) => `✓ ${name}`)
      .join("\n");

    const wellness = Object.entries(data.wellness || {})
      .map(([name, rating]) => `${name}: ${rating}/5`)
      .join("\n");

    const summary = `📅 TODAY — ${todayISO()}

🙂 Mood: ${data.mood || "Not recorded"}
😴 Sleep: ${data.sleep || "Not recorded"} hours

🏋️ HABITS
${completed || "None completed"}

🧠 WELLNESS
${wellness || "Not recorded"}`;

    try {
      await api("/journal", {
        method: "POST",
        body: JSON.stringify({
          entry_date: todayISO(),
          content: summary
        })
      });
      notify("🔥 Today's check-in sent to Telegram!");
    } catch (e) {
      notify("Failed to send today's check-in");
    }
  }

  return (
    <main>
      <header className="hero">
        <div>
          <div className="date-label">
            {new Date().toLocaleDateString("en-IN", {
              weekday: "long",
              month: "long",
              day: "numeric",
            })}
          </div>
          <h1>Good evening 👋</h1>
          <p>Let's check in with yourself.</p>
        </div>

        <div className="avatar">S</div>
      </header>

      <Card className="mood-card">
        <SectionTitle eyebrow="DAILY CHECK-IN" title="How are you feeling?" />

        <div className="mood-row">
          {moods.map(([emoji, label]) => (
            <button
              key={emoji}
              className={`mood-button ${
                data.mood === emoji ? "selected" : ""
              }`}
              onClick={() => saveMood(emoji)}
            >
              <span>{emoji}</span>
              <small>{label}</small>
            </button>
          ))}
        </div>
      </Card>

      <div className="grid-two">
        <Card>
          <div className="mini-heading">
            <span>😴</span>
            <div>
              <div className="eyebrow">SLEEP</div>
              <strong>{data.sleep.toFixed(1)}h</strong>
            </div>
          </div>

          <input
            className="range"
            type="range"
            min="0"
            max="12"
            step="0.5"
            value={data.sleep}
            onChange={(e) => saveSleep(Number(e.target.value))}
          />

          <div className="range-labels">
            <span>0h</span>
            <span>6h</span>
            <span>12h</span>
          </div>
        </Card>

        <Card>
          <div className="habit-summary">
            <ProgressRing value={completed} total={habits.length} />
            <div>
              <div className="eyebrow">HABITS</div>
              <strong>{completed} completed</strong>
              <p>Keep the streak alive.</p>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <SectionTitle eyebrow="TODAY" title="Your habits" />

        <div className="habit-grid">
          {habits.map(([id, emoji, name]) => (
            <button
              key={id}
              className={`habit-pill ${data.habits[id] ? "done" : ""}`}
              onClick={() => toggleHabit(id)}
            >
              <span>{emoji}</span>
              <span>{name}</span>
              <b>{data.habits[id] ? "✓" : "+"}</b>
            </button>
          ))}
        </div>
      </Card>

      <Card>
        <SectionTitle eyebrow="WELLNESS" title="Rate your day" />

        <div className="wellness-list">
          {wellness.map(([emoji, name]) => (
            <div className="wellness-item" key={name}>
              <div className="wellness-name">
                <span>{emoji}</span>
                {name}
              </div>

              <div className="rating-row">
                {[1, 2, 3, 4, 5].map((rating) => (
                  <button
                    key={rating}
                    className={
                      data.wellness[name] >= rating ? "rating active" : "rating"
                    }
                    onClick={() => saveWellness(name, rating)}
                  >
                    {rating}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="priority-card">
        <div className="priority-icon">🎯</div>
        <div>
          <div className="eyebrow">THIS WEEK</div>
          <h3>{data.priority || "Set your top priority"}</h3>
          <p>Small progress every day adds up.</p>
        </div>
      </Card>

      <Card className="ai-card">
        <div className="ai-icon">✦</div>
        <div>
          <div className="eyebrow">AI INSIGHT</div>
          <h3>{data.insight}</h3>
          <p>Your personal data is being turned into useful patterns.</p>
        </div>
      </Card>
    
        <button className="primary-button" onClick={submitToday}>
          📲 Submit Today's Check-in
        </button>

</main>
  );
}

function Month({ data, setData, notify }) {
  const [shoppingInput, setShoppingInput] = useState("");

  async function addShopping() {
    if (!shoppingInput.trim()) return;

    const item = {
      id: Date.now(),
      text: shoppingInput.trim(),
      done: false,
    };

    setData((d) => ({
      ...d,
      shopping: [...d.shopping, item],
    }));

    setShoppingInput("");

    try {
      await api("/shopping-item", {
        method: "POST",
        body: JSON.stringify({
          month_start: monthISO(),
          item: item.text,
        }),
      });
      notify("Shopping item added");
    } catch {
      notify("Added locally");
    }
  }

  return (
    <main>
      <header className="page-header">
        <div>
          <div className="eyebrow">MONTHLY COMMAND CENTER</div>
          <h1>
            {new Date().toLocaleDateString("en-IN", {
              month: "long",
              year: "numeric",
            })}
          </h1>
        </div>
      </header>

      <div className="focus-grid">
        <Card className="focus-card">
          <span className="big-icon">🎯</span>
          <div className="eyebrow">FOCUS ON</div>
          <h3>{data.focus || "Build. Learn. Grow."}</h3>
          <p>Keep your attention on what actually matters.</p>
        </Card>

        <Card className="focus-card distraction">
          <span className="big-icon">🚫</span>
          <div className="eyebrow">DISTRACTIONS</div>
          <h3>Doomscrolling & procrastination</h3>
          <p>Protect your time and energy.</p>
        </Card>
      </div>

      <Card className="affirmation">
        <div className="big-icon">✨</div>
        <div className="eyebrow">MONTHLY AFFIRMATION</div>
        <h2>
          {data.affirmation ||
            "I am becoming more disciplined every single day."}
        </h2>
      </Card>

      <Card>
        <SectionTitle
          eyebrow="MONEY"
          title="August budget"
          action={<span className="link">View analysis →</span>}
        />

        <div className="money-grid">
          <div>
            <small>Income</small>
            <strong>₹{data.budget.income.toLocaleString("en-IN")}</strong>
          </div>
          <div>
            <small>Spent</small>
            <strong>₹{data.budget.spent.toLocaleString("en-IN")}</strong>
          </div>
          <div>
            <small>Saved</small>
            <strong>₹{data.budget.saved.toLocaleString("en-IN")}</strong>
          </div>
        </div>

        <div className="budget-bar">
          <span
            style={{
              width: `${
                data.budget.income
                  ? Math.min(
                      100,
                      (data.budget.saved / data.budget.income) * 100
                    )
                  : 0
              }%`,
            }}
          />
        </div>
      </Card>

      <Card>
        <SectionTitle eyebrow="SHOPPING" title="Things to buy" />

        <div className="add-row">
          <input
            value={shoppingInput}
            onChange={(e) => setShoppingInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addShopping()}
            placeholder="Add something..."
          />
          <button onClick={addShopping}>+</button>
        </div>

        <div className="shopping-list">
          {data.shopping.map((item) => (
            <button
              key={item.id}
              className={`shopping-item ${item.done ? "done" : ""}`}
              onClick={() =>
                setData((d) => ({
                  ...d,
                  shopping: d.shopping.map((x) =>
                    x.id === item.id ? { ...x, done: !x.done } : x
                  ),
                }))
              }
            >
              <span>{item.done ? "✓" : "○"}</span>
              {item.text}
            </button>
          ))}
        </div>
      </Card>
    </main>
  );
}

function Track({ data, setData }) {
  const days = ["M", "T", "W", "T", "F", "S", "S"];

  return (
    <main>
      <header className="page-header">
        <div>
          <div className="eyebrow">YOUR PATTERNS</div>
          <h1>Track</h1>
        </div>
      </header>

      <Card className="stats-card">
        <div>
          <div className="eyebrow">CURRENT STREAK</div>
          <strong className="huge-number">12</strong>
          <p>days of showing up 🔥</p>
        </div>

        <ProgressRing value={8} total={12} />
      </Card>

      <Card>
        <SectionTitle eyebrow="HABITS" title="This week" />

        <div className="week-days">
          {days.map((day, index) => (
            <div key={index} className={index < 5 ? "day active" : "day"}>
              <span>{day}</span>
              <b>{index < 5 ? "✓" : "·"}</b>
            </div>
          ))}
        </div>

        <div className="tracking-list">
          {habits.slice(0, 8).map(([id, emoji, name], index) => (
            <div className="tracking-row" key={id}>
              <span>{emoji}</span>
              <div className="tracking-name">{name}</div>
              <div className="dots">
                {days.map((_, day) => (
                  <span
                    key={day}
                    className={day <= Math.min(index % 7 + 2, 6) ? "filled" : ""}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <SectionTitle eyebrow="MOOD" title="Recent mood" />

        <div className="mood-calendar">
          {Array.from({ length: 14 }).map((_, i) => (
            <div key={i}>
              <small>{i + 1}</small>
              <span>{moods[i % moods.length][0]}</span>
            </div>
          ))}
        </div>
      </Card>
    </main>
  );
}

function Journal({ data, setData, notify }) {
  const [entry, setEntry] = useState(data.journal);

  async function saveJournal() {
    setData((d) => ({ ...d, journal: entry }));

    try {
      await api("/journal", {
        method: "POST",
        body: JSON.stringify({
          entry_date: todayISO(),
          content: entry,
        }),
      });
      notify("Journal saved 📝");
    } catch {
      notify("Journal saved locally");
    }
  }

  return (
    <main>
      <header className="page-header">
        <div>
          <div className="eyebrow">YOUR SPACE</div>
          <h1>Journal</h1>
        </div>
      </header>

      <Card className="journal-card">
        <div className="journal-date">
          {new Date().toLocaleDateString("en-IN", {
            weekday: "long",
            month: "long",
            day: "numeric",
          })}
        </div>

        <h2>How was today?</h2>

        <textarea
          value={entry}
          onChange={(e) => setEntry(e.target.value)}
          placeholder="Write whatever is on your mind..."
        />

        <button className="primary-button" onClick={saveJournal}>
          Save Entry
        </button>
      </Card>

      <Card>
        <SectionTitle eyebrow="MONTHLY REFLECTION" title="August" />

        {[
          ["🏆", "My Accomplishments"],
          ["🙏", "Things I'm Grateful For"],
          ["💡", "Discoveries"],
          ["🔄", "What Could I Have Done Better?"],
        ].map(([icon, title]) => (
          <div className="reflection-row" key={title}>
            <span>{icon}</span>
            <div>
              <strong>{title}</strong>
              <p>Tap to reflect...</p>
            </div>
            <span>›</span>
          </div>
        ))}
      </Card>
    </main>
  );
}

function AI({ data }) {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "ai",
      text: "Hey 👋 I'm keeping an eye on your patterns. Ask me anything about your journal, habits, mood, sleep or month.",
    },
  ]);

  async function send() {
    if (!message.trim()) return;

    const text = message.trim();

    setMessages((m) => [...m, { role: "user", text }]);
    setMessage("");

    try {
      const result = await api("/", {
        method: "POST",
        body: JSON.stringify({
          message: text,
        }),
      });

      setMessages((m) => [
        ...m,
        {
          role: "ai",
          text:
            result?.response ||
            result?.message ||
            result?.insight ||
            "Your AI response was received.",
        },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: "ai",
          text: data.insight,
        },
      ]);
    }
  }

  return (
    <main className="ai-page">
      <header className="page-header">
        <div>
          <div className="eyebrow">YOUR PERSONAL AI</div>
          <h1>AI Companion ✦</h1>
        </div>
      </header>

      <Card className="ai-hero">
        <div className="ai-orb">✦</div>
        <h2>Your patterns tell a story.</h2>
        <p>
          I can help you understand your habits, mood, productivity,
          finances and progress.
        </p>
      </Card>

      <div className="chat">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            {m.text}
          </div>
        ))}
      </div>

      <div className="chat-input">
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask about your month..."
        />
        <button onClick={send}>↑</button>
      </div>
    </main>
  );
}

export default function App() {
  const [page, setPage] = useState("today");
  const [toast, setToast] = useState("");

  const [data, setData] = useState(() => {
    const saved = localStorage.getItem("journal_frontend_data");

    return (
      JSON.parse(saved || "null") || {
        mood: "",
        sleep: 7.5,
        habits: {},
        wellness: {},
        priority: "Finish the things that matter.",
        insight:
          "You've been showing up consistently. Keep building momentum.",
        focus: "Coding, health, agency & opportunities",
        affirmation:
          "I am becoming more disciplined every single day.",
        shopping: [
          { id: 1, text: "Guitar strings", done: false },
          { id: 2, text: "USB-C cable", done: true },
          { id: 3, text: "New notebook", done: false },
        ],
        budget: {
          income: 25000,
          spent: 8400,
          saved: 16600,
        },
        journal: "",
      }
    );
  });

  useEffect(() => {
    localStorage.setItem("journal_frontend_data", JSON.stringify(data));
  }, [data]);

  useEffect(() => {
    api(`/status/${todayISO()}`)
      .then((result) => {
        if (!result) return;

        setData((d) => ({
          ...d,
          ...result,
        }));
      })
      .catch(() => {});
  }, []);

  function notify(message) {
    setToast(message);
    setTimeout(() => setToast(""), 2200);
  }

  const content = useMemo(() => {
    if (page === "month") {
      return <Month data={data} setData={setData} notify={notify} />;
    }

    if (page === "track") {
      return <Track data={data} setData={setData} />;
    }

    if (page === "journal") {
      return <Journal data={data} setData={setData} notify={notify} />;
    }

    if (page === "ai") {
      return <AI data={data} />;
    }

    return <Today data={data} setData={setData} notify={notify} />;
  }, [page, data]);

  return (
    <div className="app">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <div className="app-shell">
        {content}

        <nav className="bottom-nav">
          {[
            ["today", "⌂", "Today"],
            ["month", "◷", "Month"],
            ["track", "◌", "Track"],
            ["journal", "✎", "Journal"],
            ["ai", "✦", "AI"],
          ].map(([id, icon, label]) => (
            <button
              key={id}
              className={page === id ? "nav-active" : ""}
              onClick={() => setPage(id)}
            >
              <span>{icon}</span>
              <small>{label}</small>
            </button>
          ))}
        </nav>
      </div>

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
