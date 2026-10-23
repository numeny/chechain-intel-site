const menuBtn = document.getElementById("menuBtn");
const navLinks = document.getElementById("navLinks");

if (menuBtn && navLinks) {
  menuBtn.addEventListener("click", () => {
    const open = navLinks.classList.toggle("open");
    menuBtn.setAttribute("aria-expanded", String(open));
  });

  navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      navLinks.classList.remove("open");
      menuBtn.setAttribute("aria-expanded", "false");
    });
  });
}

const year = document.getElementById("year");
if (year) year.textContent = String(new Date().getFullYear());

const demoData = Array.isArray(window.DEMO_DATA) ? window.DEMO_DATA : [];
const demoBody = document.getElementById("demoBody");
const demoCount = document.getElementById("demoCount");

if (demoBody && demoCount) {
  const search = document.getElementById("demoSearch");
  const country = document.getElementById("demoCountry");
  const brand = document.getElementById("demoBrand");
  const state = document.getElementById("demoState");
  const reset = document.getElementById("demoReset");
  const more = document.getElementById("demoMore");
  let visible = 12;

  const states = [...new Set(demoData.map((row) => row.region).filter(Boolean))].sort((a, b) =>
    a.localeCompare(b, "zh-CN")
  );
  states.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    state.appendChild(option);
  });

  const locationOf = (row) => [row.city, row.region].filter(Boolean).join(" · ") || "—";

  const render = () => {
    const query = (search.value || "").trim().toLowerCase();
    const countryValue = country.value;
    const brandValue = brand.value;
    const stateValue = state.value;

    const filtered = demoData.filter((row) => {
      if (countryValue && row.country !== countryValue) return false;
      if (brandValue && !(row.brands || "").includes(brandValue)) return false;
      if (stateValue && row.region !== stateValue) return false;
      if (query) {
        const haystack = [row.name, row.city, row.region, row.brands, row.group, row.country_label]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(query)) return false;
      }
      return true;
    });

    demoCount.textContent = `显示 ${Math.min(visible, filtered.length)} / ${filtered.length} 条匹配 · 共 ${demoData.length} 条演示数据`;
    more.hidden = filtered.length <= visible;
    demoBody.replaceChildren();

    if (!filtered.length) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = 7;
      td.textContent = "没有匹配的记录，换个筛选条件试试。";
      td.style.color = "#9fb3c4";
      td.style.padding = "24px 16px";
      tr.appendChild(td);
      demoBody.appendChild(tr);
      return;
    }

    const fragment = document.createDocumentFragment();
    filtered.slice(0, visible).forEach((row) => {
      const tr = document.createElement("tr");
      [row.name, row.country_label, row.type, locationOf(row), row.brands || "—", row.group || "—"].forEach((value) => {
        const td = document.createElement("td");
        td.textContent = value;
        tr.appendChild(td);
      });
      const sourceCell = document.createElement("td");
      if (row.source_url) {
        const link = document.createElement("a");
        link.href = row.source_url;
        link.target = "_blank";
        link.rel = "noopener";
        link.textContent = "来源";
        sourceCell.appendChild(link);
      } else {
        sourceCell.textContent = "—";
      }
      tr.appendChild(sourceCell);
      fragment.appendChild(tr);
    });
    demoBody.appendChild(fragment);
  };

  const onFilter = () => {
    visible = 12;
    render();
  };

  [search, country, brand, state].forEach((element) => {
    element.addEventListener("input", onFilter);
    element.addEventListener("change", onFilter);
  });

  reset.addEventListener("click", () => {
    search.value = "";
    country.value = "";
    brand.value = "";
    state.value = "";
    visible = 12;
    render();
  });

  more.addEventListener("click", () => {
    visible += 12;
    render();
  });

  render();
}
