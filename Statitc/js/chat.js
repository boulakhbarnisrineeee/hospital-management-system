// Chatbot Assistant (Frontend only) — KILEWA GPT Clinic

(function () {
  const $ = (sel, root=document) => root.querySelector(sel);

  // Elements
  const launcher = document.createElement('button');
  launcher.className = 'kg-chat-launcher';
  launcher.setAttribute('aria-label','Ouvrir le chatbot');
  launcher.innerHTML = '💬';

  const panel = document.createElement('div');
  panel.className = 'kg-chat-panel';
  panel.innerHTML = `
    <div class="kg-chat-header">
      <div class="title">Assistant de la Clinique</div>
      <button class="close" aria-label="Fermer">✕</button>
    </div>
    <div class="kg-chat-body" id="kg-body" role="log" aria-live="polite"></div>
    <div class="kg-chat-footer">
      <input class="kg-input" id="kg-input" placeholder="Écrivez votre question..." />
      <button class="kg-send" id="kg-send">Envoyer</button>
    </div>
  `;

  document.body.appendChild(launcher);
  document.body.appendChild(panel);

  const body = $('#kg-body', panel);
  const input = $('#kg-input', panel);
  const sendBtn = $('#kg-send', panel);
  const closeBtn = $('.close', panel);

  // === n8n integration BEGIN ===
  const N8N_URL = 'http://localhost:5678/webhook-test/chatbot-router';
  const ALLOWED_INTENTS = new Set([
    "patient_menu","patient_rdv","patient_dashboard","patient_auth","faq_patient",
    "med_menu","med_register","med_login","faq_med",
    "admin_menu","admin_register","admin_login","faq_admin","infos"
  ]);

  async function askN8N(question) {
    const res = await fetch(N8N_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    if (!res.ok) throw new Error('n8n error');
    return await res.json();
  }

  function renderFromN8N(data) {
    const payload = data && data.output ? data.output : data; // Structured Output Parser
    const text = (payload && typeof payload.text === 'string') ? payload.text : '';
    const choices = Array.isArray(payload?.choices)
      ? payload.choices.filter(c => c && c.label && ALLOWED_INTENTS.has(c.intent)).slice(0,4)
      : [];
    if (!text) throw new Error('bad payload');
    bot(text, choices);
  }
  // === n8n integration END ===

  // UI toggle
  const open = () => { panel.style.display = 'flex'; launcher.style.display='none'; input.focus(); };
  const close = () => { panel.style.display = 'none'; launcher.style.display='flex'; };
  launcher.addEventListener('click', open);
  closeBtn.addEventListener('click', close);

  // Helpers
  function bot(text, choices=[]) {
    const wrap = document.createElement('div'); wrap.className='kg-msg bot';
    const bubble = document.createElement('div'); bubble.className='kg-bubble'; bubble.innerHTML = text;
    wrap.appendChild(bubble);

    if (choices.length) {
      const box = document.createElement('div'); box.className='kg-choices';
      choices.forEach(c=>{
        const chip = document.createElement('button'); chip.className='kg-chip'; chip.textContent=c.label;
        chip.addEventListener('click', ()=> handleIntent(c.intent));
        box.appendChild(chip);
      });
      bubble.appendChild(box);
    }

    body.appendChild(wrap);
    body.scrollTop = body.scrollHeight;
  }

  function user(text) {
    const wrap = document.createElement('div'); wrap.className='kg-msg user';
    const bubble = document.createElement('div'); bubble.className='kg-bubble'; bubble.textContent = text;
    wrap.appendChild(bubble);
    body.appendChild(wrap);
    body.scrollTop = body.scrollHeight;
  }

  // Intents (parcours guidés)
  function start() {
    bot(
      `<b>Bonjour !</b><br/>Je peux vous aider à vous orienter 👇`,
      [
        {label:'Espace Patient', intent:'patient_menu'},
        {label:'Espace Médecin', intent:'med_menu'},
        {label:'Espace Admin', intent:'admin_menu'},
        {label:'Infos & Contact', intent:'infos'},
      ]
    );
  }

  function handleIntent(intent) {
    switch (intent) {
      case 'patient_menu':
        bot(
          `Que souhaitez-vous faire en tant que <b>Patient</b> ?`,
          [
            {label:'Prendre un rendez-vous', intent:'patient_rdv'},
            {label:'Voir mes rendez-vous', intent:'patient_dashboard'},
            {label:"S'inscrire / Se connecter", intent:'patient_auth'},
            {label:'FAQ Patients', intent:'faq_patient'},
          ]
        );
        break;

      case 'patient_rdv':
        bot(`Parfait ! Cliquez ici pour accéder au formulaire de rendez-vous : <br/><a href="/patientform">/patientform</a>`);
        break;

      case 'patient_dashboard':
        bot(`Voici votre tableau de bord patient : <br/><a href="/dashboard">/dashboard</a>`);
        break;

      case 'patient_auth':
        bot(`Pour commencer : <br/>
          ➤ Connexion : <a href="/login">/login</a><br/>
          ➤ Inscription : <a href="/register">/register</a>`);
        break;

      case 'faq_patient':
        bot(
          `Questions fréquentes (Patients) :<br/>
          • Comment annuler un rendez-vous ? → Depuis <a href="/dashboard">/dashboard</a>, bouton <i>Annuler</i>.<br/>
          • Confirmation par e-mail ? → Oui, vous recevez un e-mail via nos workflows n8n.<br/>
          • Données stockées où ? → Dans Google Sheets sécurisé (lecture interne).`
        );
        break;

      case 'med_menu':
        bot(
          `Section <b>Médecin</b> :`,
          [
            {label:'Créer un compte', intent:'med_register'},
            {label:'Se connecter', intent:'med_login'},
            {label:'FAQ Médecins', intent:'faq_med'},
          ]
        );
        break;

      case 'med_register':
        bot(`Créer un compte médecin : <a href="/registermed">/registermed</a>`);
        break;

      case 'med_login':
        bot(`(À compléter si tu as une page /loginmed)`);
        break;

      case 'faq_med':
        bot(`FAQ Médecins :<br/>
             • Accès planning : à partir de votre dashboard médecin (à venir).<br/>
             • Notifications : configurables via n8n (e-mail).`);
        break;

      case 'admin_menu':
        bot(
          `Section <b>Admin</b> :`,
          [
            {label:'Créer un compte', intent:'admin_register'},
            {label:'Se connecter', intent:'admin_login'},
            {label:'FAQ Admin', intent:'faq_admin'},
          ]
        );
        break;

      case 'admin_register':
        bot(`Créer un compte administrateur : <a href="/registeradmin">/registeradmin</a>`);
        break;

      case 'admin_login':
        bot(`(À compléter si tu as une page /loginadmin)`);
        break;

      case 'faq_admin':
        bot(`FAQ Admin :<br/>
             • Gestion des utilisateurs via Google Sheets/n8n.<br/>
             • Tableaux de bord consolidation (à venir).`);
        break;

      case 'infos':
        bot(`📍 Clinique KILEWA — Adresse & contact dans le footer.<br/>
             💡 Respect & confort au cœur de nos priorités.<br/>
             ⏱️ Horaires : Lun–Sam 08:00–19:00.`);
        break;

      default:
        bot(`Je n’ai pas compris, voulez-vous réessayer ?`);
    }
  }

  // Free text → matching simple (fallback local)
  function handleFreeText(text) {
    const t = text.toLowerCase();
    if (t.includes('rendez') || t.includes('rdv')) return handleIntent('patient_rdv');
    if (t.includes('dashboard') || t.includes('voir')) return handleIntent('patient_dashboard');
    if (t.includes('patient')) return handleIntent('patient_menu');
    if (t.includes('médecin') || t.includes('medecin')) return handleIntent('med_menu');
    if (t.includes('admin')) return handleIntent('admin_menu');
    if (t.includes('contact') || t.includes('info')) return handleIntent('infos');
    // fallback
    bot(`Je peux vous guider vers Patient / Médecin / Admin, ou répondre à une FAQ.`, [
      {label:'Espace Patient', intent:'patient_menu'},
      {label:'Espace Médecin', intent:'med_menu'},
      {label:'Espace Admin', intent:'admin_menu'},
      {label:'Infos & Contact', intent:'infos'},
    ]);
  }

  // Events
  sendBtn.addEventListener('click', async () => {
    const val = input.value.trim();
    if (!val) return;
    user(val);
    input.value = '';
    try {
      const data = await askN8N(val);
      renderFromN8N(data);
    } catch (e) {
      // si n8n/Gemini ne répond pas → fallback local
      handleFreeText(val);
    }
  });
  input.addEventListener('keydown', (e)=> {
    if (e.key === 'Enter') { sendBtn.click(); }
  });

  // First open message
  let greeted = false;
  launcher.addEventListener('click', () => {
    if (!greeted) { start(); greeted = true; }
  });

})();
