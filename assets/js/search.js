/** GTA VI Ultimate Guide · search.js — recherche globale client-side */
'use strict';
(function () {
  const { $, $$, onReady, debounce } = window.GTA6;
  const SITE_ROOT = location.pathname.includes('/pages/') ? '../../' : '';

  /* Index compact : pages + items clés (enrichi au fil du build) */
  const SEARCH_INDEX = [
    { title: 'Accueil — Vue d\'ensemble', url: 'index.html', tag: 'Page', kw: 'accueil gta vi sortie 19 novembre 2026 prix editions vice city' },
    { title: 'Histoire — L\'épopée de Leonida', url: 'pages/histoire/index.html', tag: 'Histoire', kw: 'histoire synopsis jason lucia conspiration leonida penthouse' },
    { title: 'Missions — Timeline interactive', url: 'pages/histoire/missions.html', tag: 'Missions', kw: 'missions histoire walkthrough soluce difficulté récompense' },
    { title: 'Synopsis détaillé', url: 'pages/histoire/synopsis.html', tag: 'Histoire', kw: 'synopsis scénario bonnie clyde leonida conspiration' },
    { title: 'Fins alternatives', url: 'pages/histoire/fins.html', tag: 'Histoire', kw: 'fin finale endings spoiler choix relation Jason Lucia profil criminel investissements sauvegarde' },
    { title: 'Jason Duval — Profil', url: 'pages/personnages/jason.html', tag: 'Personnage', kw: 'jason duval protagoniste leonida keys army brian heder switching acteur non confirmé' },
    { title: 'Lucia Caminos — Profil', url: 'pages/personnages/lucia.html', tag: 'Personnage', kw: 'lucia caminos protagoniste liberty city leonida penitentiary Manni L Perez Game Awards nomination' },
    { title: 'Personnages secondaires', url: 'pages/personnages/secondaires.html', tag: 'Personnages', kw: 'boobie ike dre\'quan real dimez raul bautista cal hampton brian heder lori DWNPLY' },
    { title: 'Carte interactive — Liens de cartes communautaires', url: 'pages/carte/carte-interactive.html', tag: 'Carte', kw: 'carte interactive map Leonida pin carte communautaire collectibles recherche filtres six intel map-6 gta6map' },
    { title: 'Carte de Leonida — six régions', url: 'pages/carte/index.html', tag: 'Carte', kw: 'carte Leonida officielle imprimable 19 novembre atlas communautaire GitHub 3431 enregistrements fuite poster 6 régions Vice City keys Grassrivers Ambrosia Port Gellhorn Kalaga' },
    { title: 'Vice City — repères confirmés', url: 'pages/carte/vice-city.html', tag: 'Région', kw: 'Vice City Ocean Beach Little Cuba Tisha-Wocka VC Port carte Art Deco port cruise market' },
    { title: 'Leonida Keys — Key Lento', url: 'pages/carte/leonida-keys.html', tag: 'Région', kw: 'Leonida Keys Key Lento Brian Boat Works Marina Rusty Anchor plongée ponts archipel carte' },
    { title: 'Grassrivers — marais & mangroves', url: 'pages/carte/grassrivers.html', tag: 'Région', kw: 'grassrivers wetlands mangroves alligators airboat marais zones humides herbes eau danger atlas communauté' },
    { title: 'Port Gellhorn — côte oubliée', url: 'pages/carte/port-gellhorn.html', tag: 'Région', kw: 'port gellhorn starlet motel delights cabaret motels attractions fermées côte tourisme' },
    { title: 'Ambrosia — raffinerie & gang local', url: 'pages/carte/ambrosia.html', tag: 'Région', kw: 'ambrosia allied crystal sugar refinery sucre champs canne gang biker motards clewiston' },
    { title: 'Mount Kalaga — parc national', url: 'pages/carte/mount-kalaga.html', tag: 'Région', kw: 'mount kalaga national park parc chasse pêche offroad tout terrain faune forêt nord leonida' },
    { title: 'Arsenal — armes de GTA VI', url: 'pages/armes/index.html', tag: 'Armes', kw: 'armes arsenal gta vi armes confirmées noms rockstar screenshots extended look reviews presse portage silencieux arme de poing fusil shotgun' },
    { title: 'Pistolets & revolvers — ES9, K17, Morgan', url: 'pages/armes/pistolets.html', tag: 'Armes', kw: 'pistolet pistolets revolvers sidearm girardi es9 jason klose k17 lucia hawk little morgan nipper 38 capo mustang 357 silencieux visée focus' },
    { title: 'Fusils & carabines — Duke 556', url: 'pages/armes/fusils.html', tag: 'Armes', kw: 'fusil fusils carabine duke 556 extended look rifle armes longues conseils combat loadout' },
    { title: 'Explosifs — lance-grenades', url: 'pages/armes/explosifs.html', tag: 'Armes', kw: 'explosifs grenade lance-grenades rotatif launcher grenadeur munitions combat conseils' },
    { title: 'Mêlée & combat rapproché', url: 'pages/armes/melee.html', tag: 'Armes', kw: 'melee mêlée corps à corps batte couteau crowbar pied de biche queue billard marteau blocage contre focus' },
    { title: 'Véhicules — Garage de Leonida', url: 'pages/vehicules/index.html', tag: 'Véhicules', kw: 'véhicules voitures garage sport suv moto bateau hélicoptère avion conduite customisation Rockstar confirmés' },
    { title: 'Voitures — conduite, vol & garages', url: 'pages/vehicules/voitures.html', tag: 'Véhicules', kw: 'voiture voitures cheetah emerus tempesta buccaneer coquette manana stanier ganado conduite vol garage tuner tuning customisation tracker' },
    { title: 'Motos — Dinka Enduro', url: 'pages/vehicules/motos.html', tag: 'Véhicules', kw: 'moto motos bike motorcycle Dinka Enduro dirt bike motocross conduite reviews maniabilité' },
    { title: 'Bateaux & nautique — Squalo, Kayak', url: 'pages/vehicules/bateaux.html', tag: 'Véhicules', kw: 'bateau bateaux nautique squalo shitzu crest kayak remorque speedboat jet ski airboat navigation' },
    { title: 'Avions — vol & pilotage', url: 'pages/vehicules/avions.html', tag: 'Véhicules', kw: 'avion avions pilotage plane aircraft hydravion dodo jet vol review commandes' },
    { title: 'Hélicoptères — rotor & pilotage', url: 'pages/vehicules/helicopteres.html', tag: 'Véhicules', kw: 'hélicoptère hélicoptères hélico maverick buzzard rotor pilotage dégâts review' },
    { title: 'Gameplay — Hub de Leonida', url: 'pages/gameplay/index.html', tag: 'Gameplay', kw: 'gameplay mécaniques wanted 6 étoiles criminal profile braquage police focus progression' },
    { title: 'Mécaniques — Focus & progression', url: 'pages/gameplay/mecaniques.html', tag: 'Gameplay', kw: 'mécaniques focus santé stamina endurance force sommeil nutrition profil criminel criminal profile activités progression' },
    { title: 'Police & Heat — évasion', url: 'pages/gameplay/police.html', tag: 'Gameplay', kw: 'police wanted 6 étoiles évasion heat zone témoins CCTV vêtements voiture masque stars recherche wanted level' },
    { title: 'Économie', url: 'pages/gameplay/economie.html', tag: 'Gameplay', kw: 'argent économie braquage boutiques coffres safe codes aléatoires sacs butin receleurs fences revente marked bills sécurité jammer banque chapitre 3'  },
    { title: 'Combat — Focus, couverture et arsenal', url: 'pages/gameplay/combat.html', tag: 'Gameplay', kw: 'combat arme fusillade focus vulnérabilités couverture visée précision silencieux équipement conseils' },
    { title: 'Conduite — voitures, vol et garages', url: 'pages/gameplay/conduite.html', tag: 'Gameplay', kw: 'conduite pilotage voitures véhicules Waink scan vol tracker alarmes garage classes conduite conseils' },
    { title: 'Collectibles — observations & méthode', url: 'pages/collectibles/index.html', tag: 'Collectibles', kw: 'collectibles cartes collector cards scan téléphone magazines curiosités street art cartes à collectionner sets séries 480 18 cartes PowerPyx trophée 100 pour cent vendre variantes couleurs doublons'},
    { title: 'Localisations rapportées — cartes Vice City Flamingos', url: 'pages/collectibles/localisation.html', tag: 'Collectibles', kw: 'localisations lieux position carte Vice City Flamingos Julian Cruz Mateo Caballero Ulysses Whitlock Little Cuba La Perle Tequesta PowerPyx'},
    { title: 'Guide 100 % — checklist vérifiable', url: 'pages/guide/100-pour-cent.html', tag: 'Guide', kw: '100% complétion progression checklist collectibles activités missions preuves tracker local localStorage voitures véhicules modèles scannés animaux étudiés défis sauvegarde JSON tâches personnalisées'},
    { title: 'Guides GTA VI — hub', url: 'pages/guide/index.html', tag: 'Guide', kw: 'hub guides liste débutant astuces 100% trophées collectibles codes gameplay online' },
    { title: 'Premières heures — guide débutant sans spoilers', url: 'pages/guide/debutants.html', tag: 'Guide', kw: 'débutant premières heures focus Waink scan voiture coffre tenues nourriture exploration police conseils Kotaku VGC' },
    { title: 'Astuces & stratégies', url: 'pages/guide/astuces.html', tag: 'Guide', kw: 'astuces tips novices strategie argent evasion police débutant focus cache argent plancher VGC GameSpot Kotaku repas repos entrainement transports publics braquages sacs piégés lancement date heure NZ' },
    { title: 'Codes de triche', url: 'pages/guide/cheats.html', tag: 'Guide', kw: 'cheats codes triche money weapon' },
    { title: 'Bugs & glitches — signalements et précautions', url: 'pages/guide/bugs-glitches.html', tag: 'Guide', kw: 'bugs glitch crash plantage softlock écran noir sauvegarde bloquée correctif patch Reddit solutions anecdotes argent money glitch' },
    { title: 'Trophées & succès', url: 'pages/guide/trophees.html', tag: 'Guide', kw: 'trophées ps5 succès xbox platine 55 méditation missable Lucia chapitre 1 sauvegarde manuelle checklist' },
    { title: 'GTA VI Online — statut officiel', url: 'pages/online/index.html', tag: 'Online', kw: 'online multijoueur statut solo date officielle inconnue Rockstar' },
    { title: 'Économie Online — annonces et inconnues', url: 'pages/online/economie-online.html', tag: 'Online', kw: 'économie monnaie GTA VI Online microtransactions GTA+ Shark Cards monnaie premium prix service solo pas annoncé'},
    { title: 'Modes GTA VI — solo, coopération et cross-play', url: 'pages/online/modes.html', tag: 'Online', kw: 'modes solo coop coopération multijoueur crossplay progression transfert GTA Online rumeur date non annoncée' },
    { title: 'Soundtrack & radios', url: 'pages/soundtrack/index.html', tag: 'Audio', kw: 'musique soundtrack justice radio cocoteo flash fm chamber album flower in a hurricane' },
    { title: 'Éditions Standard/Ultimate', url: 'pages/editions/index.html', tag: 'Acheter', kw: 'édition standard ultimate prix 79,99 99,99 vintage vice city pack grotti chevalier' },
    { title: 'Actualités', url: 'pages/news/index.html', tag: 'News', kw: 'news actualités metacritic 99 reviews embargo sortie live' },
    { title: 'Secrets & découvertes — index sourcé', url: 'pages/secrets/index.html', tag: 'Secrets', kw: 'secrets découvertes easter eggs bugs glitches rumeurs preuves retail guide index'},
    { title: 'Glitches & bugs — signalements non confirmés', url: 'pages/secrets/glitches.html', tag: 'Secrets', kw: 'glitch bug exploit argent money glitch duplication crash softlock Reddit correctif patch'},
    { title: 'Easter eggs & secrets', url: 'pages/secrets/easter-eggs.html', tag: 'Secrets', kw: 'easter egg secret mystère référence Vice City vérification preuve capture retail rumeur théorie communauté' },
    { title: 'Quiz Leonida', url: 'pages/quiz/index.html', tag: 'Quiz', kw: 'quiz test 30 trente questions chronomètre score record localStorage sources preuves officiel presse guide tiers Reddit GitHub' }
  ];

  function normalize(str) {
    return str.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); // U+0300–U+036F
  }

  function initSearch() {
    const input = $('.site-search');
    if (!input) return;
    const wrap = input.closest('.search-wrap');
    let results = wrap.querySelector('.search-results');
    if (!results) {
      results = document.createElement('div');
      results.className = 'search-results';
      results.setAttribute('role', 'listbox');
      results.setAttribute('aria-hidden', 'true');
      wrap.appendChild(results);
    }
    let active = -1, current = [];

    const render = items => {
      current = items; active = -1;
      if (!items.length) { results.setAttribute('aria-hidden', 'true'); return; }
      results.innerHTML = items.map((it, i) =>
        `<a class="sr-item" role="option" href="${SITE_ROOT}${it.url}" data-i="${i}"><span class="sr-tag">${it.tag}</span><span>${it.title}</span></a>`
      ).join('');
      results.setAttribute('aria-hidden', 'false');
    };
    const update = debounce(() => {
      const q = normalize(input.value.trim());
      if (q.length < 2) return render([]);
      const hits = SEARCH_INDEX
        .map(it => ({ it, score: (normalize(it.title).includes(q) ? 3 : 0) + (normalize(it.kw).includes(q) ? 2 : 0) + (normalize(it.tag).includes(q) ? 1 : 0) }))
        .filter(x => x.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 8)
        .map(x => x.it);
      render(hits);
    }, 120);

    input.addEventListener('input', update);
    input.addEventListener('focus', update);
    input.addEventListener('keydown', e => {
      if (results.getAttribute('aria-hidden') === 'true') return;
      const items = $$('.sr-item', results);
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        active = (active + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
        items.forEach((el, i) => el.classList.toggle('active', i === active));
      } else if (e.key === 'Enter' && active >= 0) {
        window.location.href = items[active].getAttribute('href');
      } else if (e.key === 'Escape') {
        results.setAttribute('aria-hidden', 'true'); input.blur();
      }
    });
    document.addEventListener('click', e => { if (!wrap.contains(e.target)) results.setAttribute('aria-hidden', 'true'); });
  }

  onReady(initSearch);
})();
