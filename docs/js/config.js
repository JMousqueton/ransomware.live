window.$docsify = {      
    coverpage: false,
    subMaxLevel: 2,
    loadSidebar: true,
    routerMode: 'hash', 
    themeColor: '#42b983',
    darklightTheme: {
      defaultTheme : 'light'
                    },
    noEmoji: false,
    auto2top: true,
    autoHeader: false,
    name: '🏴‍☠️💰 Ransomware.live',
    logo: 'ransomwarelive.png',
    externalLinkTarget: '_blank',
    loadNavbar : false, // IMPORTANT
    // changelog : 'CHANGELOG.md',
    matomo: {
        host: '//stats.mousqueton.io',
        id: 10,
      },
    tabs: {
    persist    : false,
    sync       : false 
          },
    repo: 'https://github.com/jmousqueton/ransomware.live',  
    alias: {
          '/.*/_sidebar.md': '/_sidebar.md'
    },
    search: 'auto',
    search : [
    '/profiles'            // => /profiles.md
    ],
    scrollToTop: {
      auto: true,
      text: '⬆',
      right: 15,
      bottom: 15,
      offset: 500
    },
    charty: {
    "theme": "#42b983",
    "mode":  "light",
    "debug": false
 },
    'flexible-alerts': {
        style: 'callout'
    },
    plugins: [],
    footer: {
      // copy: 'Ransomware.live © 2022-2023 All Rights Reserved. ',
        copy: 'Ransomware.live © 2022-2023 is licensed under <a href="http://creativecommons.org/licenses/by-nc/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">CC BY-NC 4.0<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/nc.svg?ref=chooser-v1"></a> ',
        auth: ' ',
      pre: '<hr/>',
      style: 'text-align: right;',
    },
    progress: {
        position: "top",
        color: "var(--theme-color,#42b983)",
        height: "5px",
    }
  };
