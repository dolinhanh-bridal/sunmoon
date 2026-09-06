<script>
(function(){
  /* ---- config: connect the trial form here (Google Apps Script / Formspree / your API). Leave empty until ready. ---- */
  var FORM_ENDPOINT = '';

  var d=document, w=window;
  var reduce = w.matchMedia && w.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var LANGS={vi:'Tiếng Việt',en:'English',zh:'中文'};
  var MSG={
    en:{sending:'Sending…',btn:'Book a trial class',
        ok:function(x){return '<b>Thank you, '+x.parent+'.</b>We have your request for a trial ('+x.group+'). We will contact you on '+x.phone+' to arrange a time.';},
        no:function(x){return '<b>Almost there.</b>Our online form is not connected yet. Please send this to us on Zalo or by phone so we can arrange the trial: <br><br><em>'+x.parent+' · '+x.phone+' · '+x.group+(x.age?' · age '+x.age:'')+'</em>';},
        open:'Open menu',close:'Close menu'},
    vi:{sending:'Đang gửi…',btn:'Đăng ký học thử',
        ok:function(x){return '<b>Cảm ơn '+x.parent+'.</b>SunMoon đã nhận yêu cầu học thử ('+x.group+'). Chúng tôi sẽ liên hệ số '+x.phone+' để hẹn giờ.';},
        no:function(x){return '<b>Gần xong rồi.</b>Form online chưa được kết nối. Bạn gửi giúp thông tin này qua Zalo hoặc điện thoại để SunMoon hẹn buổi học thử: <br><br><em>'+x.parent+' · '+x.phone+' · '+x.group+(x.age?' · '+x.age+' tuổi':'')+'</em>';},
        open:'Mở menu',close:'Đóng menu'},
    zh:{sending:'发送中…',btn:'预约试听课',
        ok:function(x){return '<b>谢谢您，'+x.parent+'。</b>我们已收到您的试听申请（'+x.group+'）。我们会通过 '+x.phone+' 联系您安排时间。';},
        no:function(x){return '<b>就快好了。</b>在线表格尚未连接。请通过 Zalo 或电话把以下信息发给我们，以便安排试听：<br><br><em>'+x.parent+' · '+x.phone+' · '+x.group+(x.age?' · '+x.age+' 岁':'')+'</em>';},
        open:'打开菜单',close:'关闭菜单'}
  };
  var lang='vi';
  function esc(s){ return String(s).replace(/[&<>"']/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }

  /* ---------- language switching ---------- */
  var app=d.getElementById('app');
  function pick(){
    var q=(location.search.match(/[?&]lang=(en|vi|zh)/)||[])[1]; if(q) return q;
    var h=(location.hash.match(/lang=(en|vi|zh)/)||[])[1]; if(h) return h;
    try{ var s=localStorage.getItem('sunmoon-lang'); if(s && LANGS[s]) return s; }catch(e){}
    var n=(navigator.language||'').toLowerCase();
    if(n.indexOf('zh')===0) return 'zh';
    return 'vi';
  }
  function setLang(code, keepScroll){
    if(!LANGS[code]) code='vi';
    var tpl=d.getElementById('tpl-'+code);
    if(tpl){ app.innerHTML=tpl.innerHTML; }
    lang=code;
    d.documentElement.lang = code==='zh'?'zh-Hans':code;
    d.documentElement.setAttribute('data-lang',code);
    try{ localStorage.setItem('sunmoon-lang',code); }catch(e){}
    d.querySelectorAll('.langs button').forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.lang===code?'true':'false'); });
    init();
  }
  function bindSwitch(){
    d.querySelectorAll('.langs button').forEach(function(b){
      b.addEventListener('click', function(){ if(b.dataset.lang!==lang){ var y=w.scrollY; setLang(b.dataset.lang); w.scrollTo(0,y); } });
    });
  }

  /* ---------- page behaviours (re-run after each language swap) ---------- */
  var scrollBound=false;
  function init(){
    var header=d.querySelector('.header');
    function onScroll(){ header.classList.toggle('scrolled', w.scrollY>8); }
    onScroll();
    if(!scrollBound){ w.addEventListener('scroll', function(){ var h=d.querySelector('.header'); if(h) h.classList.toggle('scrolled', w.scrollY>8); }, {passive:true}); scrollBound=true; }

    /* mobile drawer */
    var burger=d.querySelector('.burger'), drawer=d.getElementById('drawer');
    function setMenu(open){
      burger.setAttribute('aria-expanded', open?'true':'false');
      burger.setAttribute('aria-label', open?MSG[lang].close:MSG[lang].open);
      drawer.classList.toggle('open', open);
      d.body.style.overflow = open?'hidden':'';
    }
    burger.addEventListener('click', function(){ setMenu(burger.getAttribute('aria-expanded')!=='true'); });
    drawer.querySelectorAll('a').forEach(function(a){ a.addEventListener('click', function(){ setMenu(false); }); });
    d.addEventListener('keydown', function(e){ if(e.key==='Escape' && drawer.classList.contains('open')) setMenu(false); });

    /* reveal on scroll — elements already in view are never hidden */
    var reveals=[].slice.call(d.querySelectorAll('.reveal'));
    if(!reduce && 'IntersectionObserver' in w){
      var vh=w.innerHeight;
      reveals.forEach(function(el){ if(el.getBoundingClientRect().top > vh*0.92) el.classList.add('pending'); });
      var io=new IntersectionObserver(function(entries){
        entries.forEach(function(en){
          if(en.isIntersecting){ en.target.classList.remove('pending'); en.target.classList.add('in'); io.unobserve(en.target); }
        });
      },{rootMargin:'0px 0px -8% 0px', threshold:0.08});
      reveals.forEach(function(el){ io.observe(el); });
      d.querySelectorAll('.prog-grid,.qcards,.tgrid,.sgrid').forEach(function(g){
        [].forEach.call(g.children, function(c,i){ c.style.transitionDelay=(i*90)+'ms'; });
      });
    }else{
      reveals.forEach(function(el){ el.classList.add('in'); });
    }

    /* timeline: light the dots one by one */
    var tl=d.getElementById('timeline');
    if(tl && 'IntersectionObserver' in w){
      var tio=new IntersectionObserver(function(entries){
        if(entries[0].isIntersecting){
          tl.classList.add('in');
          [].forEach.call(tl.querySelectorAll('.tl'), function(item,i){ setTimeout(function(){ item.classList.add('lit'); }, reduce?0:200+i*220); });
          tio.disconnect();
        }
      },{threshold:0.25});
      tio.observe(tl);
    }

    /* floating CTA: show after hero, hide while the form is visible */
    var fc=d.getElementById('floatCta'), hero=d.querySelector('.hero'), form=d.getElementById('trial');
    var heroGone=false, formVisible=false;
    function updateFloat(){ fc.classList.toggle('show', heroGone && !formVisible); }
    if('IntersectionObserver' in w){
      new IntersectionObserver(function(e){ heroGone=!e[0].isIntersecting; updateFloat(); },{threshold:0.15}).observe(hero);
      new IntersectionObserver(function(e){ formVisible=e[0].isIntersecting; updateFloat(); },{threshold:0.1}).observe(form);
    }

    /* accordion: close others when one opens */
    var acc=d.querySelectorAll('.acc details');
    acc.forEach(function(det){
      det.addEventListener('toggle', function(){ if(det.open) acc.forEach(function(o){ if(o!==det) o.open=false; }); });
    });

    /* gallery lightbox */
    var shots=[].slice.call(d.querySelectorAll('.gallery .shot, .hero-visual .shot'));
    shots.forEach(function(s){ s.addEventListener('click', function(){ openBox(s); }); });
    function openBox(s){
      var bg=getComputedStyle(s).backgroundImage; var big=(bg.match(/url\("?(.*?)"?\)/)||[])[1]; if(!big) return;
      var box=d.createElement('div'); box.className='lightbox';
      box.innerHTML='<button class="close" aria-label="Close">×</button><img src="'+big+'" alt="">';
      d.body.appendChild(box); d.body.style.overflow='hidden';
      function kill(){ box.remove(); d.body.style.overflow=''; d.removeEventListener('keydown',onk); }
      function onk(e){ if(e.key==='Escape') kill(); }
      box.addEventListener('click', kill); d.addEventListener('keydown', onk);
      requestAnimationFrame(function(){ box.classList.add('on'); });
    }

    /* trial form */
    form.addEventListener('submit', function(e){
      e.preventDefault();
      var ok=true;
      ['f-parent','f-phone'].forEach(function(id){
        var inp=d.getElementById(id), f=inp.closest('.field');
        var bad = !inp.value.trim();
        f.classList.toggle('invalid', bad); if(bad) ok=false;
      });
      if(!ok){ form.querySelector('.invalid input').focus(); return; }
      var data={}; new FormData(form).forEach(function(v,k){ data[k]=v; });
      data.submitted_at=new Date().toISOString(); data.lang=lang;
      var safe={}; for(var k in data) safe[k]=esc(data[k]);
      var done=form.querySelector('.done'), btn=form.querySelector('button[type=submit]');
      function finish(sent){
        form.classList.add('sent');
        done.innerHTML = sent ? MSG[lang].ok(safe) : MSG[lang].no(safe);
        done.scrollIntoView({behavior: reduce?'auto':'smooth', block:'center'});
      }
      if(!FORM_ENDPOINT){ finish(false); return; }
      btn.disabled=true; btn.textContent=MSG[lang].sending;
      fetch(FORM_ENDPOINT,{method:'POST',mode:'no-cors',headers:{'Content-Type':'text/plain'},body:JSON.stringify(data)})
        .then(function(){ finish(true); }).catch(function(){ finish(false); })
        .finally(function(){ btn.disabled=false; btn.textContent=MSG[lang].btn; });
    });
    form.querySelectorAll('input').forEach(function(i){ i.addEventListener('input', function(){ i.closest('.field').classList.remove('invalid'); }); });

    d.getElementById('year').textContent=new Date().getFullYear();
    bindSwitch();
  }

  var first=pick();
  if(first!=='vi'){ setLang(first); } else { setLang('vi'); }
})();
</script>
