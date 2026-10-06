Markdown# INTERSECT // CTF Platform - Comprehensive Technical Reference



A self-hosted, Hack The Box / CTFd style Capture-The-Flag training platform featuring a FastAPI backend, vanilla JavaScript frontend, container-orchestrated challenge sandboxes, dynamic score decay, and an inventory of 100+ vulnerable security labs.



\---



\## 1. System Architecture \& High-Level Data Flow



The platform follows a decoupled client-server architecture paired with an on-demand container orchestration layer designed to give each participant an isolated, disposable practice environment.



+-------------------------------------------------------------------------+|                           Client Browser                                ||  - Vanilla JS SPA (Routing, State Management, Terminal Boot Animation)  |+------------------------------------+------------------------------------+| HTTPS / JSON (Bearer JWT)v+------------------------------------+------------------------------------+|                        FastAPI Core Backend                             ||  - /auth (Registration, Login, RBAC)                                    ||  - /challenges (Catalog discovery, effective score calculation)         ||  - /instances (Per-user container lifecycle \& TTL enforcement)          ||  - /submissions (Cryptographic flag validation \& decay algorithm)       ||  - /scoreboard (Dynamic leaderboard recomputation)                      |+-------------------+---------------------------------+-------------------+|                                 |v                                 v+-------------------+-------------+     +-------------+-------------------+|         Persistence Layer       |     |      Orchestration Engine       ||  - SQLite (WAL Mode, PRAGMA FK) |     |  - Docker SDK / Local Engine    ||  - SQLAlchemy 2.0 Models        |     |  - Port Allocation (30000-40000)||  - Users, Teams, Challenges     |     |  - TTL Countdown \& Reaper Task  ||  - Live Instances \& Submissions |     |  - Cgroup Caps (256MB RAM)      |+---------------------------------+     +-------------+-------------------+|v+-------------+-------------------+|  Isolated Challenge Sandbox     ||  - Ephemeral Docker Container   ||  - Non-root Execution User      ||  - Unique Flag Env Injection    |+---------------------------------+

\### Complete Workflow:

1\. \*\*Authentication\*\*: Player authenticates via `POST /auth/login`, receives a signed JWT token containing the user identity (`sub`).

2\. \*\*Catalog Discovery\*\*: Client queries `GET /challenges/`, receiving active challenges with real-time decayed point values.

3\. \*\*Machine Spawning\*\*: Clicking "Start Machine" triggers `POST /instances/{id}/start`. The orchestrator scans for available host ports (range: `30000-40000`), generates a user-instance unique flag, mounts the container onto `ctf\_challenge\_net`, and begins a 45-minute TTL countdown.

4\. \*\*Vulnerability Exploitation\*\*: Player attacks the target service running on the allocated port, extracts the injected environment flag.

5\. \*\*Submission \& Verification\*\*: Flag submitted via `POST /submissions/`. Backend validates it strictly against the current active instance issued to that user.

6\. \*\*Decay Recomputation\*\*: A solve triggers dynamic point decay; scoreboard rankings update dynamically on next fetch.



\---



\## 2. Directory \& Component Structure



```text

anti\_ctf/

├── start.py                            # Multi-platform convenience runner

├── run.ps1                             # PowerShell execution wrapper

└── ctf-platform/

&#x20;   ├── ctf.db                          # Primary SQLite database (WAL mode)

&#x20;   ├── backend/

&#x20;   │   ├── Dockerfile                  # API server container image definition

&#x20;   │   ├── requirements.txt            # Pinned Python dependencies

&#x20;   │   ├── app/

&#x20;   │   │   ├── main.py                 # FastAPI application factory \& lifecycle

&#x20;   │   │   ├── schemas.py              # Pydantic data validation schemas

&#x20;   │   │   ├── core/

&#x20;   │   │   │   ├── config.py           # Environment settings \& defaults

&#x20;   │   │   │   ├── db.py               # SQLAlchemy database engine session

&#x20;   │   │   │   └── security.py         # Bcrypt hashing \& JWT token utilities

&#x20;   │   │   ├── models/

&#x20;   │   │   │   └── models.py           # Relational ORM schemas

&#x20;   │   │   ├── api/

&#x20;   │   │   │   ├── auth.py             # User access \& profile endpoints

&#x20;   │   │   │   ├── challenges.py       # Catalog query \& metadata endpoints

&#x20;   │   │   │   ├── instances.py        # Lifecycle control for sandboxes

&#x20;   │   │   │   ├── submissions.py      # Validation \& rate-limiting logic

&#x20;   │   │   │   └── scoreboard.py       # Live scoreboard ranking queries

&#x20;   │   │   └── services/

&#x20;   │   │       ├── orchestrator.py     # Docker container manager \& reaper

&#x20;   │   │       ├── flag\_generator.py   # Cryptographic flag generation

&#x20;   │   │       ├── scoring.py          # Dynamic point decay implementation

&#x20;   │   │       └── seeder.py           # Disk-to-database catalog synchronizer

&#x20;   │   └── tests/

&#x20;   │       └── test\_platform.py        # End-to-end integration test suite

&#x20;   ├── frontend/

&#x20;   │   ├── index.html                  # Single-page application shell

&#x20;   │   ├── app.js                      # UI routing, state, and terminal animations

&#x20;   │   └── styles.css                  # Dark investigation case-file design system

&#x20;   ├── challenges/                     # 101 self-contained challenge directories

&#x20;   │   └── <category>-<slug>/

&#x20;   │       ├── challenge.yaml          # Registration metadata \& point configs

&#x20;   │       ├── Dockerfile              # Hardened container build configuration

&#x20;   │       └── app.py                  # Vulnerable application source code

&#x20;   └── infra/

&#x20;       └── docker-compose.platform.yml # Unified production container deployment

3\. Database Schema Models (SQLAlchemy ORM)1. Userid: Integer primary key.username: String (unique, indexed).email: String (unique, indexed).hashed\_password: String (Bcrypt encrypted).team\_id: Integer foreign key (optional team grouping).is\_admin: Boolean flag.created\_at: DateTime.2. Teamid: Integer primary key.name: String (unique).created\_at: DateTime.3. Challengeid: Integer primary key.slug: String (unique identifier matching challenge directory name).name: Display title.category: Security domain (Web, Crypto, Pwn, Rev, Forensics, Misc, OSINT).description: Challenge prompt and operational briefing.base\_points: Initial difficulty point weight.docker\_image: Pre-built image tag.container\_port: Exposed service port inside container.flag\_env\_var: Destination environment variable name (FLAG).4. Instanceid: Integer primary key.user\_id: Integer foreign key (users.id).challenge\_id: Integer foreign key (challenges.id).host\_port: Dynamic port mapped on the Docker host machine (30000–40000).flag\_value: Unique ephemeral flag string generated for this session.status: String (running, stopped, expired).created\_at: Session start timestamp.expires\_at: Enforced session expiration timestamp (TTL).5. Submissionid: Integer primary key.user\_id: Integer foreign key (users.id).challenge\_id: Integer foreign key (challenges.id).submitted\_flag: String captured from input.is\_correct: Boolean validation status.points\_awarded: Integer reflecting points captured at submission time.submitted\_at: Timestamp (used as scoreboard tie-breaker).4. Operational MechanicsDynamic Flag ConstructionFlags are generated inside flag\_generator.py using cryptographically secure primitives:$$\\text{Random Token} = \\text{secrets.token\\\_hex}(12)$$$$\\text{Checksum} = \\text{Truncate}\_{12}(\\text{SHA-256}(\\text{slug} \\parallel \\text{user\\\_id} \\parallel \\text{Random Token}))$$$$\\text{Flag Format} = \\text{CTF}\\{\\text{challenge-slug}\\\_\\text{Random Token}\\\_\\text{Checksum}\\}$$Dynamic Score Decay AlgorithmImplemented in scoring.py, base points decay gradually based on total solve count:$$\\text{Effective Points} = \\max\\left(\\text{Base Points} \\times (1.0 - 0.03 \\times (\\text{Solves} - 1)),\\ \\max(0.3 \\times \\text{Base Points},\\ 10)\\right)$$The first solver receives 100% of the base points.Subsequent solves decrease the value by 3% per solve.Floor limit: Values never decay below 30% of base value (or 10 points).5. Complete Challenge Inventory (101 Challenges)Web Exploitation (26 Labs)web-sqli-101: Staff Login (100 Pts)web-sqli-basic: Staff Portal Authentication (100 Pts)web-headers-leak: Corporate Staging Leak (120 Pts)web-idor-customer-records: Bank Vault IDOR (150 Pts)web-ping-diagnostic: NetPulse Command Injection (150 Pts)web-type-juggling-php: PHP Magic Hash Gateway (150 Pts)web-swagger-api-leak: Undocumented API Endpoints (150 Pts)web-git-leak-recovery: Exposed Source Repository (175 Pts)web-jwt-none-alg: JWT Null Algorithm Forge (175 Pts)web-cors-misconfiguration: Origin Trust Misconfiguration (175 Pts)web-csrf-admin-change: Portal Password Resetter (175 Pts)web-xss-stored-guestbook: VIP Guestbook Stored XSS (180 Pts)web-graphql-introspection: Aether GraphQL Schema Leak (200 Pts)web-websocket-tamper: Live Stock Terminal (200 Pts)web-ssti-jinja2: Template Wizard Playground (200 Pts)web-ssrf-internal-proxy: Cloud Fetcher SSRF (225 Pts)web-nosql-mango-injection: MongoDB Operator Injection (225 Pts)web-oauth-redirect-bypass: Single Sign-On Hijack (225 Pts)web-lfi-log-poison: File View Log Poisoning (250 Pts)web-xxe-xml-entity: XML Invoice Parser XXE (250 Pts)web-sqli-blind-boolean: Blind Oracle Boolean SQLi (275 Pts)web-race-condition-coupon: Flash Sale TOCTOU Race (275 Pts)web-csp-bypass-jsonp: Strict CSP JSONP Bypass (275 Pts)web-sqli-time-based: Chronos Timing Attack (300 Pts)web-prototype-pollution: JSON Merge Prototype Pollution (300 Pts)web-pickle-deserialization: Python Pickle Keystore (300 Pts)Cryptography (20 Labs)crypto-caesar-vault: Ancient Vault Cipher (100 Pts)crypto-rail-fence-cipher: Transposition Rail Fence (100 Pts)crypto-substitution-freq: Monoalphabetic Ciphertext (125 Pts)crypto-xor-singlebyte: Single Byte XOR Stream (125 Pts)crypto-vigenere-cipher: Polyalphabetic Enigma (150 Pts)crypto-rsa-small-e: RSA Small Public Exponent (175 Pts)crypto-multibyte-xor: Repeating-Key XOR Decryptor (175 Pts)crypto-rsa-fermat-factor: Fermat Close Prime Factorization (200 Pts)crypto-one-time-pad-reuse: Two-Time Pad Key Replay (200 Pts)crypto-diffie-hellman-mitm: Diffie-Hellman Subgroup Attack (225 Pts)crypto-lcg-prng-predict: Linear Congruential Predictor (225 Pts)crypto-rsa-common-modulus: RSA Common Modulus Attack (225 Pts)crypto-aes-cbc-bitflip: AES-CBC Bit-Flipping Attack (250 Pts)crypto-aes-ecb-oracle: AES-ECB Byte-by-Byte Oracle (250 Pts)crypto-md5-collision: Hash Collision Validator (250 Pts)crypto-feistel-network: Custom Feistel Block Cipher (275 Pts)crypto-hash-length-extension: SHA-256 MAC Extension (275 Pts)crypto-rsa-wiener-attack: Wiener's Small Private Exponent (275 Pts)crypto-ecdsa-nonce-reuse: ECDSA Repeated Nonce Leak (325 Pts)crypto-padding-oracle: CBC Padding Oracle Decryptor (350 Pts)Reverse Engineering (15 Labs)rev-matrix-vault: Matrix Biometric Gatekeeper (150 Pts)rev-upx-packed-binary: Unpacking Compressed Payloads (150 Pts)rev-dotnet-cil-decompile: .NET Assembly CIL Explorer (175 Pts)rev-string-obfuscator: Polymorphic String Deobfuscation (175 Pts)rev-pyc-bytecode-decompile: Python Bytecode Recovery (175 Pts)rev-assembly-x86-trace: x86 Assembly Control Flow (200 Pts)rev-android-smali-crack: Android Smali Bytecode (225 Pts)rev-wasm-auth-core: WebAssembly Security Module (225 Pts)rev-keygenme-math: CyberKeygen Constraint Solver (250 Pts)rev-lfsr-state-reversal: LFSR Key Stream Inversion (250 Pts)rev-rust-demangling: Rust Pattern Matcher (250 Pts)rev-anti-debug-bypass: Debugger Detection Trap (275 Pts)rev-golang-binary-analysis: Stripped Go Binary Analysis (275 Pts)rev-firmware-mips-router: MIPS Router Firmware Reversal (300 Pts)rev-vm-interpreter: Custom Bytecode Virtual Machine (350 Pts)Forensics \& Incident Response (15 Labs)forensics-exif-geotag-intel: Photographic Metadata Intelligence (100 Pts)forensics-pcap-http-auth: Unencrypted HTTP Credentials (125 Pts)forensics-corrupted-png-fix: Corrupted PNG Header Repair (150 Pts)forensics-zip-password-crack: Legacy ZipCrypto Cracking (150 Pts)forensics-log-audit: Operation Phantom Beacon (150 Pts)forensics-audio-spectrogram: Sonic Spectrogram Frequency (150 Pts)forensics-stego-lsb-image: Steganographic Pixel Art (150 Pts)forensics-pdf-stream-hidden: Classified PDF Document Objects (175 Pts)forensics-pcap-dns-tunnel: DNS Exfiltration Tunnel Capture (200 Pts)forensics-disk-image-carve: Deleted File Inode Carving (225 Pts)forensics-usb-keystroke-decode: USB Keystroke HID Capture (225 Pts)forensics-registry-hivedump: Windows Registry Hive Analysis (225 Pts)forensics-windows-event-logs: Lateral Movement Event Log Audit (250 Pts)forensics-memory-volatility: Volatility Memory Triage (250 Pts)forensics-pcap-tls-keylog: TLS Decryption with SSLKEYLOG (275 Pts)Binary Exploitation (Pwn) (10 Labs)pwn-buffer-overflow-ret2win: Buffer Overflow 101: Ret2Win (150 Pts)pwn-format-string-leak: Format String Memory Leak (200 Pts)pwn-integer-overflow: Integer Overflow Memory Corruption (200 Pts)pwn-shellcode-exec: Custom Shellcode Injection (225 Pts)pwn-got-overwrite: Global Offset Table (GOT) Overwrite (275 Pts)pwn-ret2libc-nx-bypass: Ret2Libc Non-Executable Stack (275 Pts)pwn-rop-chain-builder: ROP Emporium Gadget Chain (300 Pts)pwn-use-after-free: Heap Use-After-Free (UAF) (325 Pts)pwn-heap-chunk-tamper: Heap Metadata Chunk Overwrite (350 Pts)pwn-offby-one-nullbyte: Off-by-One Poison Null Byte (350 Pts)Miscellaneous \& Sandbox Escapes (10 Labs)misc-esoteric-brainfuck: Brainfuck Code Interpreter (100 Pts)misc-base-multi-encode: Multi-Layer Base Encoding (100 Pts)misc-git-history-secret: Git Commit Time Machine (125 Pts)misc-qr-code-reconstruct: Damaged QR Code Alignment (150 Pts)misc-bash-rbash-escape: Restricted Bash (rbash) Escape (150 Pts)misc-prompt-injection-llm: AI Sentinel Prompt Injection (175 Pts)misc-linux-suid-privesc: Linux SUID Binary Escalation (175 Pts)misc-pyjail-subclasses: Python Sandbox Escape: Subclasses (200 Pts)misc-docker-socket-escape: Docker Socket Container Breakout (250 Pts)misc-pyjail-restricted-ast: Zero Characters PyJail (300 Pts)OSINT \& Reconnaissance (5 Labs)osint-public-code-leak: Public Repository Secret Leak (125 Pts)osint-certificate-transparency: Certificate Transparency Mining (150 Pts)osint-whois-historical-dns: Historical WHOIS Registrar Audit (150 Pts)osint-subdomain-takeover: Dangling CNAME Takeover (175 Pts)osint-geo-shadow-recon: Geointelligence Sun Shadow Angle (200 Pts)6. Security Hardening Analysis \& ConstraintsIntegrated ControlsHardened Cgroups: Challenge instances execute with Linux capabilities dropped, no-new-privileges enabled, capped at 256MB RAM and 128 active process threads.Non-Root Execution: Container processes run under dedicated restricted system users.Submission Throttling: Leaky bucket rate limiter enforcing a strict 15 attempts/minute limit per identity to prevent brute forcing.Process Fallback: Automatic local subprocess execution when Docker engine is not available.Production Hardening RoadmapDocker Daemon Proxy: In raw deployments, mounting the host Docker socket grants effective root privileges; production deployments should integrate docker-socket-proxy or migrate to a Kubernetes API driver.Relational Backend: The default single-file SQLite database should be replaced with managed PostgreSQL in multi-tenant competition environments.Network Isolation: Replace shared bridge networking with per-tenant overlay networks or Kubernetes NetworkPolicies.

