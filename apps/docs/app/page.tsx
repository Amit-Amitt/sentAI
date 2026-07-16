export default function DocsHomePage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        padding: "3rem",
        background:
          "radial-gradient(circle at top left, rgba(0, 164, 255, 0.15), transparent 20rem), #0d1624",
        color: "#f8fafc",
      }}
    >
      <div style={{ maxWidth: 720, textAlign: "center" }}>
        <p
          style={{
            letterSpacing: "0.24em",
            textTransform: "uppercase",
            opacity: 0.7,
            fontSize: "0.8rem",
          }}
        >
          Sentinel AI Documentation
        </p>
        <h1 style={{ fontSize: "3rem", marginTop: "1rem", marginBottom: "1rem" }}>
          Foundation workspace is ready
        </h1>
        <p style={{ lineHeight: 1.7, opacity: 0.85 }}>
          Product-facing documentation pages will be filled in once the core backend, simulation,
          and dashboard flows are implemented.
        </p>
      </div>
    </main>
  );
}
