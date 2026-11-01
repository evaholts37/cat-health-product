(function () {
  "use strict";

  const script = document.currentScript;
  const root = new URL(script.dataset.root || "./", document.baseURI);
  const tree = window.REPO_NAV_TREE || [];

  function pageKey(url) {
    const parsed = new URL(url);
    let path = parsed.pathname;
    if (path.endsWith("/")) path += "index.html";
    return parsed.origin + path;
  }

  const nav = document.createElement("nav");
  nav.id = "repo-nav";
  nav.setAttribute("aria-label", "Навігація репозиторієм");

  const heading = document.createElement("div");
  heading.className = "repo-nav-heading";
  heading.textContent = "Догляд за улюбленцями";
  nav.appendChild(heading);

  function makePages(pages) {
    const list = document.createElement("ul");
    list.className = "repo-nav-pages";

    for (const page of pages) {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = new URL(page.path, root).href;
      link.textContent = page.title;
      item.appendChild(link);
      if (page.children && page.children.length) {
        item.appendChild(makePages(page.children));
      }
      list.appendChild(item);
    }

    return list;
  }

  const branches = document.createElement("ul");
  branches.className = "repo-nav-branches";
  for (const branch of tree) {
    if (!branch.pages || !branch.pages.length) continue;
    const item = document.createElement("li");
    const label = document.createElement("span");
    label.className = "repo-nav-branch";
    label.textContent = branch.label;
    item.appendChild(label);
    item.appendChild(makePages(branch.pages));
    branches.appendChild(item);
  }
  nav.appendChild(branches);

  function updateCurrent() {
    const currentPage = pageKey(window.location.href);
    const targetId = decodeURIComponent(window.location.hash.slice(1));
    const target = targetId ? document.getElementById(targetId) : null;
    const sectionId = target?.closest("section")?.id || targetId;
    const personaArea = ["персони", "jobs", "матриця"].includes(sectionId);
    for (const link of nav.querySelectorAll("a")) {
      link.removeAttribute("aria-current");
      if (pageKey(link.href) !== currentPage) continue;
      const linkHash = decodeURIComponent(new URL(link.href).hash);
      if (!linkHash || (linkHash === "#персони" && personaArea) || (linkHash === "#ресерч" && !personaArea)) {
        link.setAttribute("aria-current", linkHash ? "location" : "page");
      }
    }
  }

  document.body.classList.add("repo-has-nav");
  document.body.insertBefore(nav, document.body.firstChild);
  updateCurrent();
  window.addEventListener("hashchange", updateCurrent);
})();
