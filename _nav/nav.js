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

  const currentPage = pageKey(window.location.href);
  const nav = document.createElement("nav");
  nav.id = "repo-nav";
  nav.setAttribute("aria-label", "Навігація репозиторієм");

  const heading = document.createElement("div");
  heading.className = "repo-nav-heading";
  heading.textContent = "Здоров'я котів";
  nav.appendChild(heading);

  function makePages(pages) {
    const list = document.createElement("ul");
    list.className = "repo-nav-pages";

    for (const page of pages) {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = new URL(page.path, root).href;
      link.textContent = page.title;
      if (pageKey(link.href) === currentPage) {
        link.setAttribute("aria-current", "page");
      }
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

  document.body.classList.add("repo-has-nav");
  document.body.insertBefore(nav, document.body.firstChild);
})();
