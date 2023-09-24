# 💰 _Ransom notes for group_ suncrypt
> 🔗 [suncrypt](group/suncrypt)
* **[suncrypt.html](https://ransomware.live/ransomware_notes/suncrypt/suncrypt.html)**

```
  <!DOCTYPE html>
<html lang="en">
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width,initial-scale=1'>
  <title></title>
  <style>
    html, body {
      background-color: #1a1a1a;
    }
    body {
      padding-top: 3rem !important;
    }
    #text h2 {
      color: white;
      font-size: 2rem;
      font-weight: 600;
      line-height: 1.125;
    }
    .tabs {
      -webkit-overflow-scrolling: touch;
      align-items: stretch;
      display: flex;
      font-size: 1rem;
      justify-content: space-between;
      overflow: hidden;
          overflow-x: hidden;
      overflow-x: auto;
      white-space: nowrap;
    }
    .tabs ul {
        align-items: center;
        border-bottom-color: #454545;
        border-bottom-style: solid;
        border-bottom-width: 1px;
        display: flex;
        flex-grow: 1;
        flex-shrink: 0;
        justify-content: flex-start;
    }  
      .tabs.is-toggle ul {
        border-bottom: none;
      }
      .tabs li {
          position: relative;
      }
      .tabs li {
          display: block;
      }      
      .tabs.is-toggle li.is-active a {
          background-color: white;
          border-color: white;
          color: rgba(0, 0, 0, 0.7);
          z-index: 1;
      }
      .tabs.is-toggle li:first-child a {
          border-top-left-radius: 3px;
          border-bottom-left-radius: 3px;
      }
      .tabs li.is-active a {
          border-bottom-color: white;
          color: white;
      }
      .tabs.is-toggle a {
          border-color: #454545;
          border-style: solid;
          border-width: 1px;
          margin-bottom: 0;
          position: relative;
      }
      .tabs a {
          align-items: center;
          border-bottom-color: #454545;
          border-bottom-style: solid;
          border-bottom-width: 1px;
          color: white;
          display: flex;
          justify-content: center;
          margin-bottom: -1px;
          padding: 0.5em 1em;
          vertical-align: top;
          cursor: pointer;
      }      
    .tabs.is-toggle li:last-child a {
        border-top-right-radius: 3px;
        border-bottom-right-radius: 3px;
    }      
    .container {
      max-width: 1152px;
      max-width: ;
      flex-grow: 1;
      margin: 0 auto;
      position: relative;
      width: auto;
    }
    .box {
      background-color: #242424;
      color: white;
      display: block;
      padding: 1.25rem;
      border: 1px solid #303030;
    }    
    blockquote {
      background: hsl(0, 0%, 20%);
      padding: 1rem;
      border-left: 3px solid #55a630;
    }
    a {
      color: #e55934;
    }
  </style>
  <script>
    let text = {
      en: `<h2> Whats Happen? </h2>
        We got your documents and files encrypted and you cannot access them. To make sure weâre not bluffing just check out your files. Want to recover them? Just do what we instruct you to. If you fail to follow our recommendations, you will never see your files again. During each attack, we copy valuable commercial data. If the user doesnât pay to us, we will either send those data to rivals, or publish them. GDPR. Donât want to pay to us, pay 10x more to the government. 

        <h2> What Guarantees? </h2>
        Weâre doing our own business and never care about what you do. All we need is to earn. Should we be unfair guys, no one would work with us. So if you drop our offer we wonât take any offense but youâll lose all of your data and files. How much time would it take to recover losses? You only may guess.

        <h2> How do I access the website? </h2>
        <ul>
          <li><a href="https://torproject.org" target="_blank">Get TOR browser here</a></li>
          <li><a href="http://ebwexiymbsib4rmw.onion/chat.html?[snap]">Go to our website</a></li>
        </ul>`,
      de: `<h2> Was ist gerade passiert? </h2>
        Wir haben Ihre Dokumente und Dateien verschlÃ¼sselt und Sie kÃ¶nnen nicht mehr darauf zugreifen. Jeder Angriff wird von einer Kopie der kommerziellen Informationen begleitet. Um sicherzustellen, dass wir es ernst meinen, prÃ¼fen Sie einfach Ihre Dateien und Sie werden sehen. MÃ¶chten Sie sie wiederherstellen? Halten Sie sich einfach an unsere Anweisungen, um uns zu bezahlen. Tuen Sie dies nicht, werden Sie Ihre Dateien niemals wiedersehen. Im Falle einer Zahlungsverweigerung werden die Daten entweder an Wettbewerber verkauft oder in offenen Quellen bereitgestellt. GDPR. Wenn Sie uns nicht bezahlen mÃ¶chten, zahlen Sie das Zehnfache an der Regierung.

        <h2> Wie sollten Sie uns trauen ? </h2>
        Wir machen unsere eigenen GeschÃ¤fte und kÃ¼mmern uns nicht darum was Sie tunen. Wir mÃ¼ssen nur verdienen. Sollten wir einfach nur bluffen, wÃ¼rde niemand an uns zahlen. Wenn Sie unser Angebot ablehnen, werden Sie alle Ihre Daten fÃ¼r immer verlieren. Wie viel Zeit werden Sie brauchen um ihre Daten selber zu ersetzen ? Sie kÃ¶nnen es sich schon denken.

        <h2> Unsere Forderungen </h2>
        <ul>
          <li><a href="https://torproject.org" target="_blank">Holen Sie sich den TOR-Browser hier</a></li>
          <li><a href="http://ebwexiymbsib4rmw.onion/chat.html?[snap]">Gehen Sie auf unsere Website</a></li>
        </ul>`,
      fr: `<h2> Qu'est-ce qui vient de se passer? </h2>
        Nous avons cryptÃ© vos documents et fichiers et vous ne pouvez pas y accÃ©der. Chaque attaque est accompagnÃ©e d'une copie des informations commerciales. Pour vous assurer que nous ne bluffons pas. Voulez-vous les restaurer? Faites juste ce que nous vous demandons, pour nous payer. Si vous ne suivez pas nos recommandations, vous ne verrez plus jamais vos fichiers. En cas de refus de paiement - les donnÃ©es seront soit revendues Ã  des concurrents, soit diffusÃ©es dans des sources ouvertes. GDPR. Si vous ne voulez pas nous payer, payez x10 fois le gouvernement.

        <h2> Qu'en est-il des garanties? </h2>
        Nous faisons nos propres affaires et ne nous soucions jamais de ce que vous faites. Tout ce dont nous avons besoin est de gagner de l'argent. Si nous devions Ãªtre injustes, personne ne travaillerait avec nous. Donc, si vous abandonnez notre offre, nous ne prendrons aucune infraction, mais vous perdrez toutes vos donnÃ©es et vos fichiers. Combien de temps faudrait-il pour rÃ©cupÃ©rer les pertes? Vous pouvez seulement deviner.

        <h2> Comment puis-je accÃ©der au site web? </h2>
        <ul>
          <li><a href="https://torproject.org" target="_blank">TÃ©lÃ©chargez le navigateur TOR ici</a></li>
          <li><a href="http://ebwexiymbsib4rmw.onion/chat.html?[snap]">Allez sur notre site web</a></li>
        </ul>`,
      es: `<h2> Â¿Lo que de pasar? </h2>
        Ya tenemos sus documentos y archivos encriptados y usted no puede acceder a ellos. Para asegurarse de que no estamos faroleando. Â¿Quiere recuperarlos? SÃ³lo haga lo que le indicamos. Si usted no sigue nuestras recomendaciones, usted nunca verÃ¡ sus archivos. Durante cada ataque, copiamos los datos comerciales valiosos. Si el usuario no nos paga, enviaremos estos datos a sus rivales o los publicaremos. GDPR. No quiere pagarnos, paga 10 veces mÃ¡s al gobierno.

        <h2> Â¿QuÃ© pasa con las garantÃ­as? </h2>
        Estamos haciendo nuestro propio negocio y nunca nos importa lo que hace usted. Todo lo que necesitamos es ganar. Hay que ser injustos chicos, nadie trabajarÃ­a con nosotros. Entonces, si deja caer nuestras propuestas, no nos ofenderemos pero usted perderÃ¡ todos sus datos y archivos. Â¿CuÃ¡nto tiempo se requiere para recuperar las pÃ©rdidas? SÃ³lo usted puede adivinar.

        <h2> Â¿CÃ³mo acceder al sitio web? </h2>
        <ul>
          <li><a href="https://torproject.org" target="_blank">Obtenga el navegador TOR aquÃ­</a></li>
          <li><a href="http://ebwexiymbsib4rmw.onion/chat.html?[snap]">Vaya a nuestro sitio web</a></li>
        </ul>`,
      jp: `<h2> ä½ããã£ãã®ã§ããï¼ </h2>
        ãã­ã¥ã¡ã³ãã¨ãã¡ã¤ã«ãæå·åãã¾ããã ãããã«ã¢ã¯ã»ã¹ãããã¨ã¯ã§ãã¾ããã ãã©ãããªãããã«ããã«ã¯ã ãã¡ã¤ã«ããã§ãã¯ã¢ã¦ããã¦ããã¹ã¦ãã ããããåå¾©ãããã§ããï¼ ãã ã
        ã
        æç¤ºãããã¨ã æç¤ºã«å¾ããªãå ´åããã¡ã¤ã«ã¯äºåº¦ã¨è¡¨ç¤ºããã¾ããã åæ»æä¸­ã«ãè²´éãªåç¨ãã¼ã¿ãã³ãã¼ãã¾ãã ã¦ã¼ã¶ã¼ãå½ç¤¾ã«æ¯æããªãå ´åã¯ããããã®ãã¼ã¿ãã©ã¤ãã«ã«éä¿¡ããããå¬éãã¾ãã

        <h2> ä½ãä¿è¨¼ããã¾ãã ? </h2>
        ç§ãã¡ã¯ç§ãã¡èªèº«ã®ãã¸ãã¹ãè¡ã£ã¦ãããããªããä½ãããããæ°ã«ãã¾ããã å¿è¦ãªã®ã¯ç¨¼ããã¨ã ãã§ãã ç§ãã¡ãä¸å¬å¹³ãªäººã§ããå ´åãèª°ãç§ãã¡ã¨ä¸ç·ã«åããã¨ã¯ããã¾ããã ã§ããããããªããç§ãã¡ã®ç³ãåºãããã¦ããç§ãã¡ã¯ä½ã®ç½ªãç¯ãã¾ãã
        ãã¹ã¦ã®ãã¼ã¿ã¨ãã¡ã¤ã«ãå¤±ããã¾ãã æå¤±ãåå¾©ããã®ã«ã©ããããæéããããã¾ããï¼ æ¨æ¸¬ããã ãã§ãã
        <h2> Webãµã¤ãã«ã¢ã¯ã»ã¹ããã«ã¯ã©ãããã°ããã§ããï¼ </h2>
        <ul>
        <li><a href=" https://torproject.org " target="_blank">ããã§ TORãã©ã¦ã¶ãå¥æ </a></li>
        <li><a href="http://ebwexiymbsib4rmw.onion/chat.html?[snap]">å½ç¤¾ã®ã¦ã§ããµã¤ãã«ã¢ã¯ã»ã¹ </a></li>
        </ul>`
    };
    function sel_lang(event) {
      let active = document.getElementsByClassName('is-active')[0];
      active.classList.remove('is-active');
      event.target.parentElement.classList.add('is-active');
      let lang = event.target.getAttribute('data-lang');
      let el = document.getElementById('text');
      el.innerHTML = text[lang];
    }
    document.addEventListener("DOMContentLoaded", ()=>{
      let el = document.getElementById('text');
      el.innerHTML = text['en'];           
    });
  </script>
</head>
<body class='pt-6'>
<div class='container'>

<div class="tabs is-toggle">
  <ul>
    <li class="is-active"><a onclick='sel_lang(event);' data-lang='en'>EN</a></li>
    <li class=""><a onclick='sel_lang(event);' data-lang='de'>DE</a></li>
    <li class=""><a onclick='sel_lang(event);' data-lang='fr'>FR</a></li>
    <li class=""><a onclick='sel_lang(event);' data-lang='es'>ES</a></li>
    <li class=""><a onclick='sel_lang(event);' data-lang='jp'>JP</a></li>
  </ul>
</div>

<div class='box'>
<div id='text'></div>
  <div style='border: 1px solid red; padding: .5rem; font-size: 1.3rem; font-weight: 500; margin: 3rem 0;'>
    <div class='title is-4'>
    In case you decide not to cooperate, your private data will be published <a style='color: #46a049; text-decoration: underline;' target='_blank' href='http://nbzzb6sa6xuura2z.onion/'>here</a> or sold.
  </div>
</div>
<div style='margin-top: 2rem;'>
<h2>Offline how-to</h2>
<p>Copy & Paste this secret message to <a href="http://ebwexiymbsib4rmw.onion">this page</a> textarea field</p>
<p><blockquote>[snip]</blockquote></p>
</div>
</div>
</div>
</body>
</html>

```


> [!TIP]> Ransomware notes are provided by [Zscaler ThreatLabz](https://github.com/threatlabz/ransomware_notes) under MIT License
> 




Last update : _Thursday 14/09/2023 23.49 (UTC)_

