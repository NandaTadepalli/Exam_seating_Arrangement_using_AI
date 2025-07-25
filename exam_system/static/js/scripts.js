// ============ STUDENT FUNCTIONS ============
function initializeStudentFilters() {
    const searchInput = document.getElementById('search');
    const deptSelect = document.getElementById('department');
    const yearSelect = document.getElementById('studyYear');
    const semSelect = document.getElementById('semester');
    const studentListBody = document.getElementById('student-list'); // Get tbody reference
    const rows = studentListBody ? Array.from(studentListBody.querySelectorAll('tr')) : []; // Get current rows
    const resetBtn = document.getElementById('resetStudentFilters');
    const printBtn = document.getElementById('printStudentBtn'); // Get print button
    const downloadBtn = document.getElementById('downloadStudentBtn'); // Get download button


    function filterRows() {
        const search = searchInput.value.trim().toLowerCase();
        const dept = deptSelect.value.trim().toLowerCase();
        const year = yearSelect.value.trim();
        const sem = semSelect.value.trim().toLowerCase();

        rows.forEach(row => {
            const cells = row.children;
            // Defensive: check if enough columns exist
            if (cells.length < 6) {
                row.style.display = 'none';
                return;
            }
            const studentId = cells[1].innerText.trim().toLowerCase();
            const name = cells[2].innerText.trim().toLowerCase();
            const department = cells[3].innerText.trim().toLowerCase();
            const studyYear = cells[4].innerText.trim();
            const semester = cells[5].innerText.trim().toLowerCase();

            // Compare department ignoring case and whitespace
            const matchSearch = !search || studentId.includes(search) || name.includes(search);
            const matchDept = dept === 'all' || department.replace(/\s+/g, '').toLowerCase() === dept.replace(/\s+/g, '').toLowerCase();
            const matchYear = year === 'all' || studyYear === year;
            const matchSem = sem === 'all' || semester === sem;

            row.style.display = (matchSearch && matchDept && matchYear && matchSem) ? '' : 'none';
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            searchInput.value = '';
            deptSelect.value = 'all';
            yearSelect.value = 'all';
            semSelect.value = 'all';
            filterRows();
        });
    }

    // --- NEW: Attach listeners for Print and Download buttons here ---
    if (printBtn) {
        printBtn.onclick = printStudentTable; // Use onclick to overwrite previous listeners
    } else {
        console.error('printStudentBtn not found after content load');
    }
    if (downloadBtn) {
        downloadBtn.onclick = downloadStudentCSV; // Use onclick to overwrite previous listeners
    } else {
        console.error('downloadStudentBtn not found after content load');
    }
    // --- END NEW ---

    // Ensure all elements exist before adding listeners to avoid errors
    if (!searchInput || !deptSelect || !yearSelect || !semSelect || !studentListBody) return;


    searchInput.addEventListener('input', filterRows);
    deptSelect.addEventListener('change', filterRows);
    yearSelect.addEventListener('change', filterRows);
    semSelect.addEventListener('change', filterRows);

    filterRows(); // Run initially
}

function printStudentTable() {
    const table = document.getElementById("student-table");
    if (!table) return;

    // Get only visible rows from the original table
    const visibleRows = Array.from(document.querySelectorAll("#student-list tr")).filter(
        row => row.style.display !== "none" && row.querySelectorAll('td').length === 9
    );
    if (!visibleRows.length) return alert("No data to print.");

    // Clone the table structure
    const cloneTable = table.cloneNode(true);
    // Remove last column (actions) from header
    const headerRow = cloneTable.querySelector("thead tr");
    if (headerRow && headerRow.children.length === 9) headerRow.removeChild(headerRow.lastElementChild);

    // Remove all rows from tbody
    const tbody = cloneTable.querySelector("tbody");
    tbody.innerHTML = "";
    // Add only visible rows, removing last cell (actions)
    visibleRows.forEach(row => {
        const cloneRow = row.cloneNode(true);
        if (cloneRow.children.length === 9) cloneRow.removeChild(cloneRow.lastElementChild);
        tbody.appendChild(cloneRow);
    });

    const newWindow = window.open("", "_blank");
    if (!newWindow) return alert("Popup blocked!");

    newWindow.document.write(`
        <html><head><title>Print Student Data</title>
        <style>
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #000; padding: 8px; text-align: left; }
            th { background-color: #1E3A5F; color: white; }
        </style></head><body>
        <h2>Student Data</h2>
        ${cloneTable.outerHTML}
        </body></html>
    `);
    newWindow.document.close();
    newWindow.focus();
    newWindow.print();
}

function downloadStudentCSV() {
    const table = document.getElementById("student-table");
    if (!table) return;

    const rows = Array.from(document.querySelectorAll("#student-list tr"))
        .filter(row => row.style.display !== "none" && row.querySelectorAll('td').length === 9);
    if (!rows.length) return alert("No data to download.");

    // Get headers except last (actions)
    const headers = Array.from(table.querySelectorAll("thead th"))
        .slice(0, 8) // Get 8 headers
        .map(th => `"${th.textContent.trim()}"`)
        .join(",");

    // Get row data except last cell (actions)
    const data = rows.map(row => {
        const cells = Array.from(row.querySelectorAll("td"));
        if (cells.length !== 9) return ""; // Ensure it has all columns before slicing
        return cells.slice(0, 8).map(td => `"${td.textContent.trim()}"`).join(",");
    }).filter(line => line); // Filter out any empty lines

    const csvContent = [headers, ...data].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "student_data.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ============ FACULTY FUNCTIONS ============
function initializeFacultyFilters() {
    const searchInput = document.getElementById("search");
    const deptSelect = document.getElementById("department");
    const facultyListBody = document.getElementById("faculty-list"); // Get tbody reference
    const rows = facultyListBody ? Array.from(facultyListBody.querySelectorAll('tr')) : []; // Get current rows
    const resetBtn = document.getElementById('resetFacultyFilters');
    const printBtn = document.getElementById('printFacultyBtn'); // Get print button
    const downloadBtn = document.getElementById('downloadFacultyBtn'); // Get download button

    function filterFaculty() {
        const search = searchInput.value.trim().toLowerCase();
        const dept = deptSelect.value.trim().toLowerCase();

        rows.forEach(row => {
            const cells = row.children;
            if (cells.length < 4) { // Minimum cells required to perform checks
                row.style.display = 'none';
                return;
            }
            const facultyId = cells[1].innerText.trim().toLowerCase();
            const name = cells[2].innerText.trim().toLowerCase();
            const department = cells[3].innerText.trim().toLowerCase();

            const matchesSearch = !search || facultyId.includes(search) || name.includes(search);
            const matchesDept = dept === "all" || department.replace(/\s+/g, '').toLowerCase() === dept.replace(/\s+/g, '').toLowerCase();

            row.style.display = (matchesSearch && matchesDept) ? "" : "none";
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            searchInput.value = '';
            deptSelect.value = 'all';
            filterFaculty();
        });
    }

    // --- NEW: Attach listeners for Print and Download buttons here ---
    if (printBtn) {
        printBtn.onclick = printFacultyTable; // Use onclick to overwrite previous listeners
    } else {
        console.error('printFacultyBtn not found after content load');
    }
    if (downloadBtn) {
        downloadBtn.onclick = downloadFacultyCSV; // Use onclick to overwrite previous listeners
    } else {
        console.error('downloadFacultyBtn not found after content load');
    }
    // --- END NEW ---

    // Ensure all elements exist before adding listeners to avoid errors
    if (!searchInput || !deptSelect || !facultyListBody) return;

    searchInput.addEventListener("input", filterFaculty);
    deptSelect.addEventListener("change", filterFaculty);
    filterFaculty(); // run initially
}


function printFacultyTable() {
    const table = document.getElementById("faculty-table");
    if (!table) return;

    const cloneTable = table.cloneNode(true);
    const headerRow = cloneTable.querySelector("thead tr");
    if (headerRow && headerRow.children.length > 0) headerRow.lastElementChild.remove(); // Remove actions header

    const visibleRows = Array.from(table.querySelectorAll("tbody tr")).filter( // Use original table for visibility
        row => row.style.display !== "none"
    );

    const tbody = cloneTable.querySelector("tbody");
    tbody.innerHTML = ""; // Clear existing rows in clone

    visibleRows.forEach(row => {
        const cloneRow = row.cloneNode(true);
        if (cloneRow.children.length > 0) cloneRow.lastElementChild.remove(); // Remove actions cell
        tbody.appendChild(cloneRow);
    });

    const newWindow = window.open("", "_blank");
    if (!newWindow) return alert("Popup blocked!");

    newWindow.document.write(`
        <html><head><title>Print Faculty Data</title>
        <style>
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #000; padding: 8px; text-align: left; }
            th { background-color: #1E3A5F; color: white; }
        </style></head><body>
        <h2>Faculty Data</h2>
        ${cloneTable.outerHTML}
        </body></html>
    `);
    newWindow.document.close();
    newWindow.focus();
    newWindow.print();
}

function downloadFacultyCSV() {
    const table = document.getElementById("faculty-table");
    if (!table) return;

    const rows = Array.from(document.querySelectorAll("#faculty-list tr"))
        .filter(row => row.style.display !== "none");

    if (!rows.length) return alert("No data to download.");

    const headers = Array.from(table.querySelectorAll("thead th"))
        .slice(0, -1) // Exclude the last header ("Actions")
        .map(th => `"${th.textContent.trim()}"`)
        .join(",");

    const data = rows.map(row => {
        return Array.from(row.querySelectorAll("td"))
            .slice(0, -1) // Exclude the last cell ("Actions")
            .map(td => `"${td.textContent.trim()}"`)
            .join(",");
    });

    const csvContent = [headers, ...data].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "faculty_data.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ============ ROOM FUNCTIONS ============
function initializeRoomFilters() {
    const searchInput = document.getElementById('room-search');
    const blockSelect = document.getElementById('room-block');
    const minCapInput = document.getElementById('capacity-min');
    const maxCapInput = document.getElementById('capacity-max');
    const resetBtn = document.getElementById('resetRoomFilters');
    const roomsListBody = document.getElementById('rooms-list'); // Get tbody reference
    const rows = roomsListBody ? Array.from(roomsListBody.querySelectorAll('tr')) : []; // Get current rows
    const printBtn = document.getElementById('printRoomBtn'); // Get print button
    const downloadBtn = document.getElementById('downloadRoomBtn'); // Get download button

    function filterRooms() {
        const search = searchInput.value.toLowerCase();
        const block = blockSelect.value;
        const minCap = parseInt(minCapInput.value) || 0;
        const maxCap = parseInt(maxCapInput.value) || Infinity;

        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 4) { // Minimum cells required to perform checks
                row.style.display = 'none';
                return;
            }
            const roomId = cells[1].textContent.toLowerCase();
            const roomBlock = cells[2].textContent.trim();
            const roomCap = parseInt(cells[3].textContent) || 0;

            const matchSearch = !search || roomId.includes(search) || roomBlock.toLowerCase().includes(search);
            const matchBlock = block === 'All' || roomBlock === block;
            const matchCapacity = roomCap >= minCap && roomCap <= maxCap;

            row.style.display = (matchSearch && matchBlock && matchCapacity) ? '' : 'none';
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            searchInput.value = '';
            blockSelect.value = 'All';
            minCapInput.value = '';
            maxCapInput.value = '';
            filterRooms();
        });
    }

    // --- NEW: Attach listeners for Print and Download buttons here ---
    if (printBtn) {
        printBtn.onclick = printRoomTable; // Use onclick to overwrite previous listeners
    } else {
        console.error('printRoomBtn not found after content load');
    }
    if (downloadBtn) {
        downloadBtn.onclick = downloadRoomCSV; // Use onclick to overwrite previous listeners
    } else {
        console.error('downloadRoomBtn not found after content load');
    }
    // --- END NEW ---

    // Ensure all elements exist before adding listeners to avoid errors
    if (!searchInput || !blockSelect || !minCapInput || !maxCapInput || !roomsListBody) return;

    searchInput.addEventListener('input', filterRooms);
    blockSelect.addEventListener('change', filterRooms);
    minCapInput.addEventListener('input', filterRooms);
    maxCapInput.addEventListener('input', filterRooms);

    filterRooms(); // run initially
}

function printRoomTable() {
    const table = document.getElementById('room-table');
    if (!table) return;

    const cloneTable = table.cloneNode(true);
    const headerRow = cloneTable.querySelector("thead tr");
    if (headerRow && headerRow.children.length > 0) headerRow.lastElementChild.remove(); // Remove actions header

    const visibleRows = Array.from(table.querySelectorAll("tbody tr")).filter( // Use original table for visibility
        row => row.style.display !== "none"
    );

    const tbody = cloneTable.querySelector("tbody");
    tbody.innerHTML = ""; // Clear existing rows in clone

    visibleRows.forEach(row => {
        const cloneRow = row.cloneNode(true);
        if (cloneRow.children.length > 0) cloneRow.lastElementChild.remove(); // Remove actions cell
        tbody.appendChild(cloneRow);
    });

    const newWindow = window.open("", "_blank");
    if (!newWindow) return alert("Popup blocked!");

    newWindow.document.write(`
        <html><head><title>Print Room Data</title>
        <style>
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #000; padding: 8px; text-align: left; }
            th { background-color: #1E3A5F; color: white; }
        </style></head><body>
        <h2>Room Data</h2>
        ${cloneTable.outerHTML}
        </body></html>
    `);
    newWindow.document.close();
    newWindow.focus();
    newWindow.print();
}

function downloadRoomCSV() {
    const table = document.getElementById('room-table');
    if (!table) return;

    const rows = Array.from(document.querySelectorAll('#rooms-list tr'))
        .filter(row => row.style.display !== 'none');

    if (!rows.length) return alert('No data to download.');

    const headers = Array.from(table.querySelectorAll('thead th'))
        .slice(0, -1) // Exclude the last header ("Actions")
        .map(th => `"${th.textContent.trim()}"`)
        .join(',');

    const data = rows.map(row => {
        return Array.from(row.querySelectorAll('td'))
            .slice(0, -1) // Exclude the last cell ("Actions")
            .map(td => `"${td.textContent.trim()}"`)
            .join(',');
    });

    const csvContent = [headers, ...data].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'rooms_data.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ============ GLOBAL INITIALIZER ============
document.addEventListener("DOMContentLoaded", () => {
    console.log('DOM fully loaded');
    // The initial call to these functions ensures filters work on first load
    // And also attaches the print/download listeners if the table is present initially.
    initializeContentScripts(window.location.pathname); // Call for the current page
});

// Function to call appropriate initialization after AJAX content load
function initializeContentScripts(pageUrl) {
    // These functions now handle attaching print/download listeners themselves.
    // They also grab the latest table rows, which is important for filtering.
    // We explicitly call them here based on the URL.

    // Student Management
    if (pageUrl.includes('/students/') && typeof initializeStudentFilters === 'function') {
        initializeStudentFilters();
    }
    // Faculty Management
    if (pageUrl.includes('/faculty/') && typeof initializeFacultyFilters === 'function') {
        initializeFacultyFilters();
    }
    // Room Management
    if (pageUrl.includes('/rooms/') && typeof initializeRoomFilters === 'function') {
        initializeRoomFilters();
    }
    // Add more conditions for other pages if they have unique JS initialization
}

