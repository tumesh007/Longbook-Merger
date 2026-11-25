/**
 * Longbook Merger Web — Print-Ready A4 Landscape PDF Generator
 * Built for CBSL & Finacle Banking Long Book Reports
 * 100% Client-Side with pdf-lib & PapaParse
 */

class LongbookMergerApp {
  constructor() {
    this.files = []; // List of { file, name, text, date, pages, isHtml, maxCols }
    this.selectedFileIndex = 0;
    this.previewPageIndex = 0;
    this.previewZoom = 1.0;

    // Options
    this.optCompactMode = true;
    this.optRemoveBlankPages = true;
    this.optGenerateIndex = true;
    this.optAutoFontSize = true;

    this.initDOM();
    this.bindEvents();
  }

  initDOM() {
    this.fileInput = document.getElementById("file-input");
    this.dropZone = document.getElementById("drop-zone");
    this.workspace = document.getElementById("workspace");
    this.emptyState = document.getElementById("empty-state");

    this.fileQueueList = document.getElementById("file-queue-list");
    this.fileCountBadge = document.getElementById("file-count-badge");
    this.btnMerge = document.getElementById("btn-merge-download");
    this.btnClearAll = document.getElementById("btn-clear-all");
    this.btnSortDates = document.getElementById("btn-sort-dates");

    // Options checkboxes
    this.chkCompact = document.getElementById("chk-compact-mode");
    this.chkBlank = document.getElementById("chk-blank-pages");
    this.chkIndex = document.getElementById("chk-generate-index");

    // Preview Pane
    this.previewContainer = document.getElementById("preview-sheet");
    this.previewHeader = document.getElementById("preview-header");
    this.previewPageInfo = document.getElementById("preview-page-info");
    this.btnPrevPage = document.getElementById("btn-prev-page");
    this.btnNextPage = document.getElementById("btn-next-page");
    this.btnZoomIn = document.getElementById("btn-zoom-in");
    this.btnZoomOut = document.getElementById("btn-zoom-out");
    this.zoomLevelEl = document.getElementById("zoom-level");

    this.toastEl = document.getElementById("toast");
    this.toastMsg = document.getElementById("toast-msg");
  }

  bindEvents() {
    if (this.fileInput) {
      this.fileInput.addEventListener("change", (e) => this.handleFileSelect(e));
    }
    if (this.dropZone) {
      this.dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        this.dropZone.classList.add("border-blue-500", "bg-blue-50/50");
      });
      this.dropZone.addEventListener("dragleave", (e) => {
        e.preventDefault();
        this.dropZone.classList.remove("border-blue-500", "bg-blue-50/50");
      });
      this.dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        this.dropZone.classList.remove("border-blue-500", "bg-blue-50/50");
        if (e.dataTransfer.files.length > 0) {
          this.loadFiles(Array.from(e.dataTransfer.files));
        }
      });
    }

    if (this.btnMerge) {
      this.btnMerge.addEventListener("click", () => this.generateMergedPdf());
    }
    if (this.btnClearAll) {
      this.btnClearAll.addEventListener("click", () => this.clearAll());
    }
    if (this.btnSortDates) {
      this.btnSortDates.addEventListener("click", () => this.sortByDate());
    }

    // Toggles
    if (this.chkCompact) {
      this.chkCompact.addEventListener("change", (e) => {
        this.optCompactMode = e.target.checked;
        this.updatePreview();
      });
    }
    if (this.chkBlank) {
      this.chkBlank.addEventListener("change", (e) => {
        this.optRemoveBlankPages = e.target.checked;
        this.updatePreview();
      });
    }
    if (this.chkIndex) {
      this.chkIndex.addEventListener("change", (e) => {
        this.optGenerateIndex = e.target.checked;
      });
    }

    // Preview navigation
    if (this.btnPrevPage) {
      this.btnPrevPage.addEventListener("click", () => this.changePreviewPage(-1));
    }
    if (this.btnNextPage) {
      this.btnNextPage.addEventListener("click", () => this.changePreviewPage(1));
    }
    if (this.btnZoomIn) {
      this.btnZoomIn.addEventListener("click", () => this.changePreviewZoom(0.15));
    }
    if (this.btnZoomOut) {
      this.btnZoomOut.addEventListener("click", () => this.changePreviewZoom(-0.15));
    }
  }

  showToast(message, isError = false) {
    if (!this.toastEl || !this.toastMsg) return;
    this.toastMsg.textContent = message;
    this.toastEl.classList.remove("hidden", "bg-slate-900", "bg-red-600");
    this.toastEl.classList.add(isError ? "bg-red-600" : "bg-slate-900");
    this.toastEl.classList.remove("opacity-0", "translate-y-4");

    setTimeout(() => {
      this.toastEl.classList.add("opacity-0", "translate-y-4");
      setTimeout(() => this.toastEl.classList.add("hidden"), 300);
    }, 3500);
  }

  async handleFileSelect(e) {
    if (e.target.files.length > 0) {
      await this.loadFiles(Array.from(e.target.files));
      e.target.value = "";
    }
  }

  async loadFiles(fileList) {
    this.showToast(`Loading ${fileList.length} file(s)...`);

    for (const file of fileList) {
      try {
        const text = await this.readFileAsText(file);
        const parsed = this.parseReport(text, file.name);
        this.files.push(parsed);
      } catch (err) {
        console.error("Failed to parse file", file.name, err);
      }
    }

    if (this.files.length > 0) {
      if (this.emptyState) this.emptyState.classList.add("hidden");
      if (this.workspace) this.workspace.classList.remove("hidden");
      this.renderQueue();
      this.selectFile(0);
      this.showToast(`Successfully added ${fileList.length} report(s).`);
    }
  }

  readFileAsText(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(reader.error);
      reader.readAsText(file, "utf-8");
    });
  }

  /**
   * Sniff and parse report text into logical pages
   */
  parseReport(rawText, fileName) {
    let cleanText = rawText;
    let isHtml = false;

    // Check if it's an HTML-wrapped report
    if (/<html|<pre|<body|<table/i.test(rawText.substring(0, 4096))) {
      isHtml = true;
      // Extract <pre> blocks if present
      const preMatches = rawText.match(/<pre[^>]*>([\s\S]*?)<\/pre>/gi);
      if (preMatches && preMatches.length > 0) {
        cleanText = preMatches
          .map((block) => block.replace(/<\/?pre[^>]*>/gi, ""))
          .join("\n\x0c\n");
      }
      // Replace &nbsp; with spaces, convert <hr> to form feeds
      cleanText = cleanText
        .replace(/&nbsp;/gi, " ")
        .replace(/<hr[^>]*>/gi, "\x0c")
        .replace(/<br\s*\/?>/gi, "\n")
        .replace(/<[^>]+>/g, ""); // Strip other tags

      // Decode entities
      const txtElem = document.createElement("textarea");
      txtElem.innerHTML = cleanText;
      cleanText = txtElem.value;
    }

    // Expand tabs to 8 spaces (standard monospaced banking report format)
    cleanText = cleanText.replace(/\t/g, "        ");

    // Split into raw pages by form feed (\x0c or \f)
    let rawPages = cleanText.split(/\x0c|\f/);

    // If no form feeds were present, fallback to splitting by repeated header
    if (rawPages.length === 1 && /Page:\s*\d+/i.test(cleanText)) {
      rawPages = cleanText.split(/(?=\s*PUNJAB NATIONAL BANK|\s*Page:\s*\d+)/);
    }

    // Process each page
    const pages = [];
    let reportDate = "";
    let maxCols = 80;

    for (let i = 0; i < rawPages.length; i++) {
      const pageText = rawPages[i];
      const lines = pageText.split(/\r?\n/);

      // Trim leading and trailing empty lines from page
      while (lines.length > 0 && lines[0].trim() === "") lines.shift();
      while (lines.length > 0 && lines[lines.length - 1].trim() === "") lines.pop();

      if (lines.length === 0) continue; // Skip completely empty pages

      // Check max column width
      for (const line of lines) {
        if (line.length > maxCols) maxCols = line.length;
      }

      // Sniff report date if not already found
      if (!reportDate) {
        const fullPageStr = lines.slice(0, 10).join(" ");
        const dateMatch = fullPageStr.match(/\b\d{2}[-/]\d{2}[-/]\d{4}\b/);
        if (dateMatch) {
          reportDate = dateMatch[0];
        }
      }

      // Check if cover page
      const isCover = this.checkIsCoverPage(lines);

      pages.push({
        lines: lines,
        isCover: isCover,
        lineCount: lines.length,
      });
    }

    return {
      fileName: fileName,
      reportDate: reportDate || "N/A",
      pages: pages,
      isHtml: isHtml,
      maxCols: Math.max(maxCols, 120),
    };
  }

  checkIsCoverPage(lines) {
    const textSample = lines.slice(0, 25).join(" ").toUpperCase();
    if (
      textSample.includes("L O N G B O O K   FOR INCUMBENT INCHARGE") ||
      textSample.includes("REPORT PARAMETERS") ||
      textSample.includes("SELECTION CRITERIA")
    ) {
      // If it doesn't contain transactions table header, it's a pure cover sheet
      if (!textSample.includes("TRAN ID") && !textSample.includes("GL SUB HEAD")) {
        return true;
      }
    }
    return false;
  }

  getActivePages(report) {
    return report.pages.filter((page) => {
      if (this.optCompactMode && page.isCover) return false;
      if (this.optRemoveBlankPages && page.lineCount === 0) return false;
      return true;
    });
  }

  renderQueue() {
    if (!this.fileQueueList) return;
    this.fileQueueList.innerHTML = "";

    this.files.forEach((fileObj, idx) => {
      const activePages = this.getActivePages(fileObj);
      const isSelected = idx === this.selectedFileIndex;

      const item = document.createElement("div");
      item.className = `file-card p-3 rounded-xl border text-xs cursor-pointer transition-all flex items-center justify-between ${
        isSelected
          ? "border-blue-500 bg-blue-50/60 shadow-sm"
          : "border-slate-200 bg-white hover:border-slate-300"
      }`;

      item.innerHTML = `
        <div class="flex items-center gap-3 overflow-hidden">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs ${
            isSelected ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-600"
          }">
            ${idx + 1}
          </div>
          <div class="truncate">
            <p class="font-semibold text-slate-800 truncate">${fileObj.fileName}</p>
            <p class="text-[11px] text-slate-500 flex items-center gap-2">
              <span>📅 ${fileObj.reportDate}</span>
              <span>•</span>
              <span>📄 ${activePages.length} pg (${fileObj.maxCols} cols)</span>
            </p>
          </div>
        </div>
        <div class="flex items-center gap-1">
          <button onclick="event.stopPropagation(); window.app.moveFile(${idx}, -1)" class="p-1 hover:bg-slate-100 rounded text-slate-400 hover:text-slate-700" title="Move Up">
            ▲
          </button>
          <button onclick="event.stopPropagation(); window.app.moveFile(${idx}, 1)" class="p-1 hover:bg-slate-100 rounded text-slate-400 hover:text-slate-700" title="Move Down">
            ▼
          </button>
          <button onclick="event.stopPropagation(); window.app.removeFile(${idx})" class="p-1 hover:bg-red-50 rounded text-slate-400 hover:text-red-600" title="Remove">
            ✕
          </button>
        </div>
      `;

      item.addEventListener("click", () => this.selectFile(idx));
      this.fileQueueList.appendChild(item);
    });

    if (this.fileCountBadge) {
      let totalPages = 0;
      this.files.forEach((f) => (totalPages += this.getActivePages(f).length));
      this.fileCountBadge.textContent = `${this.files.length} report(s) • ${totalPages} pages`;
    }
  }

  selectFile(index) {
    if (index >= 0 && index < this.files.length) {
      this.selectedFileIndex = index;
      this.previewPageIndex = 0;
      this.renderQueue();
      this.updatePreview();
    }
  }

  moveFile(index, delta) {
    const target = index + delta;
    if (target >= 0 && target < this.files.length) {
      const item = this.files.splice(index, 1)[0];
      this.files.splice(target, 0, item);
      this.selectedFileIndex = target;
      this.renderQueue();
      this.updatePreview();
    }
  }

  removeFile(index) {
    this.files.splice(index, 1);
    if (this.selectedFileIndex >= this.files.length) {
      this.selectedFileIndex = Math.max(0, this.files.length - 1);
    }
    if (this.files.length === 0) {
      this.clearAll();
    } else {
      this.renderQueue();
      this.updatePreview();
    }
  }

  clearAll() {
    this.files = [];
    this.selectedFileIndex = 0;
    this.previewPageIndex = 0;
    if (this.workspace) this.workspace.classList.add("hidden");
    if (this.emptyState) this.emptyState.classList.remove("hidden");
    this.showToast("Cleared all reports.");
  }

  sortByDate() {
    if (this.files.length <= 1) return;

    this.files.sort((a, b) => {
      const parseDate = (dStr) => {
        if (!dStr || dStr === "N/A") return 0;
        const parts = dStr.split(/[-/]/);
        if (parts.length === 3) {
          // DD-MM-YYYY to timestamp
          return new Date(`${parts[2]}-${parts[1]}-${parts[0]}`).getTime() || 0;
        }
        return 0;
      };
      return parseDate(a.reportDate) - parseDate(b.reportDate);
    });

    this.renderQueue();
    this.updatePreview();
    this.showToast("Reports sorted chronologically by date.");
  }

  changePreviewPage(delta) {
    const currentReport = this.files[this.selectedFileIndex];
    if (!currentReport) return;
    const activePages = this.getActivePages(currentReport);
    const newIdx = this.previewPageIndex + delta;

    if (newIdx >= 0 && newIdx < activePages.length) {
      this.previewPageIndex = newIdx;
      this.updatePreview();
    }
  }

  changePreviewZoom(delta) {
    this.previewZoom = Math.max(0.6, Math.min(2.0, this.previewZoom + delta));
    if (this.zoomLevelEl) {
      this.zoomLevelEl.textContent = `${Math.round(this.previewZoom * 100)}%`;
    }
    if (this.previewContainer) {
      this.previewContainer.style.transform = `scale(${this.previewZoom})`;
    }
  }

  updatePreview() {
    const currentReport = this.files[this.selectedFileIndex];
    if (!currentReport) return;

    const activePages = this.getActivePages(currentReport);

    if (this.previewPageInfo) {
      this.previewPageInfo.textContent = `Page ${this.previewPageIndex + 1} of ${activePages.length}`;
    }
    if (this.btnPrevPage) {
      this.btnPrevPage.disabled = this.previewPageIndex <= 0;
    }
    if (this.btnNextPage) {
      this.btnNextPage.disabled = this.previewPageIndex >= activePages.length - 1;
    }

    if (this.previewHeader) {
      this.previewHeader.textContent = `${currentReport.fileName} (Date: ${currentReport.reportDate} | Max Columns: ${currentReport.maxCols})`;
    }

    if (!this.previewContainer) return;

    const page = activePages[this.previewPageIndex];
    if (page) {
      this.previewContainer.textContent = page.lines.join("\n");
    } else {
      this.previewContainer.textContent = "No pages to display in this report.";
    }
  }

  /**
   * PDF Generation Engine:
   * Merges all reports into print-ready A4 Landscape PDF with exact margins and font scaling
   */
  async generateMergedPdf() {
    if (this.files.length === 0) {
      this.showToast("No reports added.", true);
      return;
    }

    try {
      this.showToast("Generating merged A4 Landscape PDF...");

      // A4 Landscape dimensions in points: 297mm x 210mm
      const A4_WIDTH = 841.89;
      const A4_HEIGHT = 595.28;

      // Margins: 8mm Left/Right, 5mm Top/Bottom
      const MARGIN_LEFT = 22.68; // 8mm
      const MARGIN_RIGHT = 22.68; // 8mm
      const MARGIN_TOP = 14.17; // 5mm
      const MARGIN_BOTTOM = 14.17; // 5mm

      const usableWidth = A4_WIDTH - MARGIN_LEFT - MARGIN_RIGHT; // 796.53 pt
      const usableHeight = A4_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM; // 566.94 pt

      const pdfDoc = await PDFLib.PDFDocument.create();
      const fontCourier = await pdfDoc.embedFont(PDFLib.StandardFonts.Courier);
      const fontCourierBold = await pdfDoc.embedFont(PDFLib.StandardFonts.CourierBold);

      // Metadata
      pdfDoc.setTitle("Merged Long Book Reports");
      pdfDoc.setAuthor("PNB LongBookMerger");
      pdfDoc.setSubject("A4 Landscape Banking Print Reports");

      // 1. Table of Contents / Index Page
      let currentPdfPageNumber = 1;
      const reportIndexEntries = [];

      // Calculate page counts and destinations
      let projectedPage = this.optGenerateIndex ? 2 : 1;
      for (const rep of this.files) {
        const pages = this.getActivePages(rep);
        const startPage = projectedPage;
        const endPage = projectedPage + pages.length - 1;
        reportIndexEntries.push({
          fileName: rep.fileName,
          date: rep.reportDate,
          pageCount: pages.length,
          startPage: startPage,
          endPage: endPage,
        });
        projectedPage += pages.length;
      }

      if (this.optGenerateIndex) {
        const indexPage = pdfDoc.addPage([A4_WIDTH, A4_HEIGHT]);
        currentPdfPageNumber++;

        // Draw Header
        indexPage.drawText("PUNJAB NATIONAL BANK — MERGED LONG BOOK INDEX", {
          x: MARGIN_LEFT,
          y: A4_HEIGHT - MARGIN_TOP - 20,
          size: 13,
          font: fontCourierBold,
          color: PDFLib.rgb(0.08, 0.15, 0.4),
        });

        const dateStr = new Date().toLocaleDateString("en-GB", {
          day: "2-digit",
          month: "short",
          year: "numeric",
        });
        indexPage.drawText(`Generated on: ${dateStr}  |  Total Reports: ${this.files.length}  |  Format: A4 Landscape (Print-Ready)`, {
          x: MARGIN_LEFT,
          y: A4_HEIGHT - MARGIN_TOP - 36,
          size: 9,
          font: fontCourier,
          color: PDFLib.rgb(0.3, 0.3, 0.3),
        });

        // Horizontal line
        indexPage.drawLine({
          start: { x: MARGIN_LEFT, y: A4_HEIGHT - MARGIN_TOP - 44 },
          end: { x: A4_WIDTH - MARGIN_RIGHT, y: A4_HEIGHT - MARGIN_TOP - 44 },
          thickness: 1,
          color: PDFLib.rgb(0.7, 0.7, 0.7),
        });

        // Table Header
        let tableY = A4_HEIGHT - MARGIN_TOP - 64;
        indexPage.drawText("Sr.No.", { x: MARGIN_LEFT, y: tableY, size: 9, font: fontCourierBold });
        indexPage.drawText("Report File Name", { x: MARGIN_LEFT + 45, y: tableY, size: 9, font: fontCourierBold });
        indexPage.drawText("Report Date", { x: MARGIN_LEFT + 460, y: tableY, size: 9, font: fontCourierBold });
        indexPage.drawText("Pages", { x: MARGIN_LEFT + 590, y: tableY, size: 9, font: fontCourierBold });
        indexPage.drawText("PDF Page Range", { x: MARGIN_LEFT + 670, y: tableY, size: 9, font: fontCourierBold });

        tableY -= 14;
        indexPage.drawLine({
          start: { x: MARGIN_LEFT, y: tableY + 8 },
          end: { x: A4_WIDTH - MARGIN_RIGHT, y: tableY + 8 },
          thickness: 0.5,
          color: PDFLib.rgb(0.8, 0.8, 0.8),
        });

        // Table Rows
        reportIndexEntries.forEach((entry, idx) => {
          tableY -= 14;
          indexPage.drawText(String(idx + 1).padStart(2, "0"), { x: MARGIN_LEFT, y: tableY, size: 8.5, font: fontCourier });
          indexPage.drawText(entry.fileName.substring(0, 55), { x: MARGIN_LEFT + 45, y: tableY, size: 8.5, font: fontCourier });
          indexPage.drawText(entry.date, { x: MARGIN_LEFT + 460, y: tableY, size: 8.5, font: fontCourier });
          indexPage.drawText(String(entry.pageCount), { x: MARGIN_LEFT + 590, y: tableY, size: 8.5, font: fontCourier });
          indexPage.drawText(`Page ${entry.startPage} - ${entry.endPage}`, { x: MARGIN_LEFT + 670, y: tableY, size: 8.5, font: fontCourierBold });
        });
      }

      // 2. Render each report page
      for (const report of this.files) {
        const pages = this.getActivePages(report);

        // Optimal font scaling for this report:
        // Width of Courier char = 0.60 * fontSize
        // We ensure maxCols * 0.60 * fontSize <= usableWidth
        const maxCols = Math.max(report.maxCols, 120);
        const maxAllowedSize = usableWidth / (maxCols * 0.60);
        const fontSize = Math.min(9.5, Math.max(5.8, maxAllowedSize));
        const lineLeading = fontSize * 1.05; // Tight leading fixes "2 papers per sheet"

        for (const page of pages) {
          const pdfPage = pdfDoc.addPage([A4_WIDTH, A4_HEIGHT]);
          let lineY = A4_HEIGHT - MARGIN_TOP - fontSize;

          for (const line of page.lines) {
            if (lineY < MARGIN_BOTTOM) break; // Safeguard against vertical overflow

            pdfPage.drawText(line, {
              x: MARGIN_LEFT,
              y: lineY,
              size: fontSize,
              font: fontCourier,
              color: PDFLib.rgb(0.05, 0.05, 0.05),
            });

            lineY -= lineLeading;
          }

          currentPdfPageNumber++;
        }
      }

      // 3. Serialize and trigger download
      const mergedBytes = await pdfDoc.save();
      const blob = new Blob([mergedBytes], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      const suffix = this.optCompactMode ? "Compact" : "Full";
      a.href = url;
      a.download = `LongBook_${suffix}_Merged_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      this.showToast(`Merged PDF downloaded (${currentPdfPageNumber - 1} pages)!`);
    } catch (err) {
      console.error("PDF Merge Error:", err);
      this.showToast("Failed to merge PDF: " + err.message, true);
    }
  }
}

// Global initialization
document.addEventListener("DOMContentLoaded", () => {
  window.app = new LongbookMergerApp();
  if (window.lucide) {
    lucide.createIcons();
  }
});
