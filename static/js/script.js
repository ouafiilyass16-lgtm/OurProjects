/**
 * Smart Parking Management System
 * Main JavaScript File
 */

// ============================================
// DATA & STATE
// ============================================

// Parking spots data
let parkingSpots = [
  { id: '1', name: 'A1', status: 'free' },
  { id: '2', name: 'A2', status: 'occupied' },
  { id: '3', name: 'A3', status: 'free' },
  { id: '4', name: 'A4', status: 'free' },
  { id: '5', name: 'B1', status: 'occupied' },
  { id: '6', name: 'B2', status: 'free' },
  { id: '7', name: 'B3', status: 'occupied' },
  { id: '8', name: 'B4', status: 'free' },
  { id: '9', name: 'C1', status: 'free' },
  { id: '10', name: 'C2', status: 'occupied' },
];

// Active tickets for gardien dashboard
const activeTickets = [
  { id: 'T001', client: 'Jean Dupont', matricule: 'AB-123-CD', spot: 'A2', entryTime: '2024-01-15 09:30' },
  { id: 'T002', client: 'Marie Martin', matricule: 'EF-456-GH', spot: 'B1', entryTime: '2024-01-15 10:15' },
  { id: 'T003', client: 'Pierre Bernard', matricule: 'IJ-789-KL', spot: 'B3', entryTime: '2024-01-15 11:00' },
  { id: 'T004', client: 'Sophie Petit', matricule: 'MN-012-OP', spot: 'C2', entryTime: '2024-01-15 11:45' },
];

// Client history
const clientHistory = [
  { date: '2024-01-10', duration: '2h 30min', amount: 25 },
  { date: '2024-01-05', duration: '1h 45min', amount: 17.5 },
  { date: '2024-01-01', duration: '3h 00min', amount: 30 },
];

// Admin data
const users = [
  { id: 1, name: 'Jean Dupont', email: 'jean@email.com', role: 'Client' },
  { id: 2, name: 'Marie Martin', email: 'marie@email.com', role: 'Client' },
  { id: 3, name: 'Pierre Bernard', email: 'pierre@email.com', role: 'Client' },
];

const vehicles = [
  { id: 1, matricule: 'AB-123-CD', marque: 'Renault', owner: 'Jean Dupont' },
  { id: 2, matricule: 'EF-456-GH', marque: 'Peugeot', owner: 'Marie Martin' },
  { id: 3, matricule: 'IJ-789-KL', marque: 'Citroën', owner: 'Pierre Bernard' },
];

// Revenue data for charts
const revenueData = [
  { day: 'Lun', revenue: 120 },
  { day: 'Mar', revenue: 150 },
  { day: 'Mer', revenue: 180 },
  { day: 'Jeu', revenue: 140 },
  { day: 'Ven', revenue: 200 },
  { day: 'Sam', revenue: 250 },
  { day: 'Dim', revenue: 180 },
];

const hourlyOccupancy = [
  { hour: '08h', rate: 30 },
  { hour: '10h', rate: 60 },
  { hour: '12h', rate: 85 },
  { hour: '14h', rate: 70 },
  { hour: '16h', rate: 55 },
  { hour: '18h', rate: 40 },
  { hour: '20h', rate: 25 },
];

// Current user state
let currentUser = JSON.parse(localStorage.getItem('currentUser')) || null;

// ============================================
// UTILITY FUNCTIONS
// ============================================

function $(selector) {
  return document.querySelector(selector);
}

function $$(selector) {
  return document.querySelectorAll(selector);
}

function formatCurrency(amount) {
  return amount.toFixed(2) + '€';
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('fr-FR');
}

function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('show');
  }, 10);

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ============================================
// MOBILE MENU
// ============================================

function initMobileMenu() {
  const menuBtn = $('#mobileMenuBtn');
  const mobileMenu = $('#mobileMenu');

  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('active');
      const icon = menuBtn.querySelector('i');
      if (icon) {
        icon.setAttribute('data-lucide',
          mobileMenu.classList.contains('active') ? 'x' : 'menu'
        );
        lucide.createIcons();
      }
    });
  }
}

// ============================================
// LOGIN PAGE
// ============================================

function initLogin() {
  const form = $('#loginForm');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const email = $('#email').value;
    const password = $('#password').value;
    const role = $('#role').value;

    // Validate email
    if (!email.includes('@')) {
      showFieldError('email', 'Veuillez entrer un email valide');
      return;
    }

    if (!password) {
      showFieldError('password', 'Mot de passe requis');
      return;
    }

    // Simulate login
    currentUser = { email, role };
    localStorage.setItem('currentUser', JSON.stringify(currentUser));

    // Redirect based on role
    redirectToDashboard(role);
  });

  // Real-time email validation
  const emailInput = $('#email');
  if (emailInput) {
    emailInput.addEventListener('blur', () => {
      if (!emailInput.value.includes('@')) {
        showFieldError('email', 'Veuillez entrer un email valide');
      } else {
        clearFieldError('email');
      }
    });
  }
}

function showFieldError(fieldId, message) {
  const field = $(`#${fieldId}`);
  const errorEl = $(`#${fieldId}Error`);

  if (field) field.classList.add('error');
  if (errorEl) {
    errorEl.textContent = message;
    errorEl.style.display = 'flex';
  }
}

function clearFieldError(fieldId) {
  const field = $(`#${fieldId}`);
  const errorEl = $(`#${fieldId}Error`);

  if (field) field.classList.remove('error');
  if (errorEl) errorEl.style.display = 'none';
}

function redirectToDashboard(role) {
  switch(role) {
    case 'client':
      window.location.href = '/client';
      break;
    case 'gardien':
      window.location.href = '/gardien';
      break;
    case 'admin':
      window.location.href = '/admin';
      break;
    default:
      window.location.href = '/';
  }
}

// ============================================
// REGISTER PAGE
// ============================================

function initRegister() {
  const form = $('#registerForm');
  if (!form) return;

  const passwordInput = $('#password');
  const strengthBar = $('#passwordStrength');
  const strengthText = $('#passwordStrengthText');

  if (passwordInput) {
    passwordInput.addEventListener('input', () => {
      updatePasswordStrength(passwordInput.value);
    });
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const name = $('#name').value;
    const email = $('#email').value;
    const password = $('#password').value;
    const role = $('#role').value;
    const acceptTerms = $('#acceptTerms').checked;

    let hasError = false;

    if (!name.trim()) {
      showFieldError('name', 'Nom requis');
      hasError = true;
    }

    if (!email.includes('@')) {
      showFieldError('email', 'Email invalide');
      hasError = true;
    }

    if (password.length < 8) {
      showFieldError('password', 'Minimum 8 caractères');
      hasError = true;
    }

    if (!acceptTerms) {
      showFieldError('acceptTerms', 'Vous devez accepter les conditions');
      hasError = true;
    }

    if (hasError) return;

    // Simulate registration
    currentUser = { name, email, role };
    localStorage.setItem('currentUser', JSON.stringify(currentUser));

    redirectToDashboard(role);
  });
}

function updatePasswordStrength(password) {
  const strengthBar = $('#passwordStrength');
  const strengthText = $('#passwordStrengthText');

  if (!strengthBar) return;

  let strength = 0;
  if (password.length > 0) strength = 25;
  if (password.length >= 6) strength = 50;
  if (password.length >= 8) strength = 75;
  if (password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password)) strength = 100;

  strengthBar.style.width = strength + '%';

  let color = 'bg-red-500';
  let text = 'Faible';

  if (strength >= 50) {
    color = 'bg-yellow-500';
    text = 'Moyenne';
  }
  if (strength >= 75) {
    color = 'bg-green-500';
    text = 'Forte';
  }

  strengthBar.className = `progress-fill ${color}`;
  if (strengthText) strengthText.textContent = `Force: ${text}`;
}

// ============================================
// CLIENT DASHBOARD
// ============================================

function initClientDashboard() {
  renderParkingGrid();
  updateStats();
  renderHistory();
  initReservationModal();
}

function renderParkingGrid() {
  const grid = $('#parkingGrid');
  if (!grid) return;

  grid.innerHTML = parkingSpots.map((spot, index) => `
    <button
      class="parking-spot ${spot.status} animate-fade-in"
      style="animation-delay: ${index * 0.03}s"
      data-spot-id="${spot.id}"
      ${spot.status !== 'free' ? 'disabled' : ''}
    >
      <i data-lucide="car" style="width: 20px; height: 20px;"></i>
      ${spot.name}
    </button>
  `).join('');

  // Add click handlers
  grid.querySelectorAll('.parking-spot.free').forEach(btn => {
    btn.addEventListener('click', () => {
      const spotId = btn.dataset.spotId;
      const spot = parkingSpots.find(s => s.id === spotId);
      openReservationModal(spot);
    });
  });

  lucide.createIcons();
}

function updateStats() {
  const freeCount = parkingSpots.filter(s => s.status === 'free').length;
  const occupiedCount = parkingSpots.filter(s => s.status === 'occupied').length;

  const freeEl = $('#freeSpots');
  const occupiedEl = $('#occupiedSpots');

  if (freeEl) freeEl.textContent = freeCount;
  if (occupiedEl) occupiedEl.textContent = occupiedCount;
}

function renderHistory() {
  const tbody = $('#historyTable');
  if (!tbody) return;

  tbody.innerHTML = clientHistory.map(item => `
    <tr>
      <td>${item.date}</td>
      <td>${item.duration}</td>
      <td class="text-right text-green-600 font-medium">${formatCurrency(item.amount)}</td>
    </tr>
  `).join('');
}

function initReservationModal() {
  const modal = $('#reservationModal');
  const closeBtn = $('#closeReservationModal');
  const cancelBtn = $('#cancelReservation');
  const confirmBtn = $('#confirmReservation');

  if (closeBtn) {
    closeBtn.addEventListener('click', closeReservationModal);
  }

  if (cancelBtn) {
    cancelBtn.addEventListener('click', closeReservationModal);
  }

  if (confirmBtn) {
    confirmBtn.addEventListener('click', confirmReservation);
  }

  // Close on overlay click
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeReservationModal();
    });
  }
}

let selectedSpotForReservation = null;

function openReservationModal(spot) {
  selectedSpotForReservation = spot;
  const modal = $('#reservationModal');
  const title = $('#reservationModalTitle');

  if (title) title.textContent = `Réserver la place ${spot.name}`;
  if (modal) modal.classList.add('active');

  // Reset form
  $('#matricule').value = '';
  $('#marque').value = '';
  $('#couleur').value = '';
}

function closeReservationModal() {
  const modal = $('#reservationModal');
  if (modal) modal.classList.remove('active');
  selectedSpotForReservation = null;
}

function confirmReservation() {
  const matricule = $('#matricule').value;

  if (!matricule) {
    showFieldError('matricule', 'Matricule requis');
    return;
  }

  if (selectedSpotForReservation) {
    // Update spot status
    const spotIndex = parkingSpots.findIndex(s => s.id === selectedSpotForReservation.id);
    if (spotIndex !== -1) {
      parkingSpots[spotIndex].status = 'occupied';

      // Re-render
      renderParkingGrid();
      updateStats();
      closeReservationModal();

      showToast('Réservation confirmée !');
    }
  }
}

// ============================================
// GARDIEN DASHBOARD
// ============================================

function initGardienDashboard() {
  renderTickets(activeTickets);
  initSearch();
  initPaymentModal();
}

function renderTickets(tickets) {
  const container = $('#ticketsList');
  if (!container) return;

  if (tickets.length === 0) {
    container.innerHTML = `
      <div class="text-center py-8 text-gray-500">
        <i data-lucide="car" style="width: 48px; height: 48px;" class="mx-auto mb-3 opacity-50"></i>
        <p>Aucun véhicule trouvé</p>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  container.innerHTML = tickets.map((ticket, index) => `
    <div
      class="ticket-card animate-slide-in-left"
      style="animation-delay: ${index * 0.05}s"
      data-ticket-id="${ticket.id}"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center">
            <i data-lucide="car" class="text-white" style="width: 24px; height: 24px;"></i>
          </div>
          <div>
            <p class="font-semibold text-parking-gray">${ticket.matricule}</p>
            <p class="text-sm text-gray-500">${ticket.client}</p>
          </div>
        </div>
        <div class="text-right">
          <p class="text-sm text-gray-500">Place ${ticket.spot}</p>
          <p class="text-sm text-gray-500">${ticket.entryTime}</p>
        </div>
      </div>
    </div>
  `).join('');

  // Add click handlers
  container.querySelectorAll('.ticket-card').forEach(card => {
    card.addEventListener('click', () => {
      const ticketId = card.dataset.ticketId;
      const ticket = activeTickets.find(t => t.id === ticketId);
      selectTicket(ticket, card);
    });
  });

  lucide.createIcons();
}

function initSearch() {
  const searchInput = $('#searchTickets');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = activeTickets.filter(t =>
      t.matricule.toLowerCase().includes(query) ||
      t.client.toLowerCase().includes(query)
    );
    renderTickets(filtered);
  });

  // Auto focus
  searchInput.focus();
}

let selectedTicket = null;

function selectTicket(ticket, cardElement) {
  selectedTicket = ticket;

  // Update UI
  document.querySelectorAll('.ticket-card').forEach(c => c.classList.remove('selected'));
  cardElement.classList.add('selected');

  // Show payment section
  const paymentSection = $('#paymentSection');
  if (paymentSection) {
    paymentSection.classList.remove('hidden');
    paymentSection.classList.add('animate-fade-in-up');
  }

  // Update amount
  const amount = calculateAmount(ticket.entryTime);
  const amountEl = $('#paymentAmount');
  const durationEl = $('#paymentDuration');

  if (amountEl) amountEl.textContent = formatCurrency(amount);
  if (durationEl) {
    const hours = Math.ceil((new Date() - new Date(ticket.entryTime)) / (1000 * 60 * 60));
    durationEl.textContent = `Durée: ${hours}h`;
  }
}

function calculateAmount(entryTime) {
  const entry = new Date(entryTime);
  const now = new Date();
  const hours = Math.max(1, Math.ceil((now - entry) / (1000 * 60 * 60)));
  return hours * 10;
}

function initPaymentModal() {
  const payBtn = $('#processPayment');
  const closeBtn = $('#closeReceiptModal');
  const closeBtn2 = $('#closeReceiptBtn');
  const printBtn = $('#printReceipt');

  if (payBtn) {
    payBtn.addEventListener('click', () => {
      openReceiptModal();
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', closeReceiptModal);
  }

  if (closeBtn2) {
    closeBtn2.addEventListener('click', closeReceiptModal);
  }

  if (printBtn) {
    printBtn.addEventListener('click', () => {
      window.print();
    });
  }
}

function openReceiptModal() {
  const modal = $('#receiptModal');
  if (!modal || !selectedTicket) return;

  // Fill receipt data
  $('#receiptTicketId').textContent = selectedTicket.id;
  $('#receiptClient').textContent = selectedTicket.client;
  $('#receiptMatricule').textContent = selectedTicket.matricule;
  $('#receiptSpot').textContent = selectedTicket.spot;
  $('#receiptEntry').textContent = selectedTicket.entryTime;
  $('#receiptExit').textContent = new Date().toLocaleString('fr-FR');
  $('#receiptAmount').textContent = formatCurrency(calculateAmount(selectedTicket.entryTime));

  modal.classList.add('active');
}

function closeReceiptModal() {
  const modal = $('#receiptModal');
  if (modal) modal.classList.remove('active');
}

// ============================================
// ADMIN DASHBOARD
// ============================================

function initAdminDashboard() {
  initTabs();
  renderUsers();
  renderVehicles();
  renderRevenueChart();
  renderOccupancyChart();
  renderOccupancyPie();
  initTarifForm();
}

function initTabs() {
  const tabs = document.querySelectorAll('.tab');
  const contents = document.querySelectorAll('.tab-content');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;

      // Update active tab
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      // Show content
      contents.forEach(c => {
        c.classList.remove('active');
        if (c.id === target) {
          c.classList.add('active');
        }
      });
    });
  });
}

function renderUsers() {
  const tbody = $('#usersTable');
  if (!tbody) return;

  tbody.innerHTML = users.map(user => `
    <tr>
      <td>#${user.id}</td>
      <td class="font-medium">${user.name}</td>
      <td>${user.email}</td>
      <td>
        <span class="badge ${user.role === 'Admin' ? 'badge-blue' : 'badge-gray'}">
          ${user.role}
        </span>
      </td>
    </tr>
  `).join('');
}

function renderVehicles() {
  const tbody = $('#vehiclesTable');
  if (!tbody) return;

  tbody.innerHTML = vehicles.map(vehicle => `
    <tr>
      <td>#${vehicle.id}</td>
      <td class="font-medium">${vehicle.matricule}</td>
      <td>${vehicle.marque}</td>
      <td>${vehicle.owner}</td>
    </tr>
  `).join('');
}

function renderRevenueChart() {
  const canvas = $('#revenueChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const width = canvas.width = canvas.offsetWidth;
  const height = canvas.height = canvas.offsetHeight;

  const padding = 40;
  const chartWidth = width - padding * 2;
  const chartHeight = height - padding * 2;

  const maxRevenue = Math.max(...revenueData.map(d => d.revenue));

  // Clear canvas
  ctx.clearRect(0, 0, width, height);

  // Draw grid lines
  ctx.strokeStyle = '#E2E8F0';
  ctx.lineWidth = 1;
  ctx.setLineDash([5, 5]);

  for (let i = 0; i <= 4; i++) {
    const y = padding + (chartHeight / 4) * i;
    ctx.beginPath();
    ctx.moveTo(padding, y);
    ctx.lineTo(width - padding, y);
    ctx.stroke();
  }

  ctx.setLineDash([]);

  // Draw line
  ctx.strokeStyle = '#38A169';
  ctx.lineWidth = 3;
  ctx.beginPath();

  revenueData.forEach((data, index) => {
    const x = padding + (chartWidth / (revenueData.length - 1)) * index;
    const y = padding + chartHeight - (data.revenue / maxRevenue) * chartHeight;

    if (index === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });

  ctx.stroke();

  // Draw points
  revenueData.forEach((data, index) => {
    const x = padding + (chartWidth / (revenueData.length - 1)) * index;
    const y = padding + chartHeight - (data.revenue / maxRevenue) * chartHeight;

    ctx.fillStyle = '#38A169';
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(x, y, 3, 0, Math.PI * 2);
    ctx.fill();

    // Draw labels
    ctx.fillStyle = '#718096';
    ctx.font = '12px Inter';
    ctx.textAlign = 'center';
    ctx.fillText(data.day, x, height - 10);
  });
}

function renderOccupancyChart() {
  const canvas = $('#occupancyChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const width = canvas.width = canvas.offsetWidth;
  const height = canvas.height = canvas.offsetHeight;

  const padding = 40;
  const chartWidth = width - padding * 2;
  const chartHeight = height - padding * 2;

  const barWidth = chartWidth / hourlyOccupancy.length * 0.6;
  const barGap = chartWidth / hourlyOccupancy.length * 0.4;

  // Clear canvas
  ctx.clearRect(0, 0, width, height);

  // Draw bars
  hourlyOccupancy.forEach((data, index) => {
    const x = padding + (barWidth + barGap) * index + barGap / 2;
    const barHeight = (data.rate / 100) * chartHeight;
    const y = padding + chartHeight - barHeight;

    // Bar
    ctx.fillStyle = '#4299E1';
    ctx.beginPath();
    ctx.roundRect(x, y, barWidth, barHeight, 4);
    ctx.fill();

    // Label
    ctx.fillStyle = '#718096';
    ctx.font = '12px Inter';
    ctx.textAlign = 'center';
    ctx.fillText(data.hour, x + barWidth / 2, height - 10);
  });
}

function renderOccupancyPie() {
  const canvas = $('#occupancyPie');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const width = canvas.width = 200;
  const height = canvas.height = 200;

  const centerX = width / 2;
  const centerY = height / 2;
  const radius = 70;
  const innerRadius = 40;

  const freeCount = parkingSpots.filter(s => s.status === 'free').length;
  const occupiedCount = parkingSpots.filter(s => s.status === 'occupied').length;
  const total = parkingSpots.length;

  const data = [
    { value: freeCount, color: '#38A169', label: 'Libres' },
    { value: occupiedCount, color: '#E53E3E', label: 'Occupées' }
  ];

  let currentAngle = -Math.PI / 2;

  data.forEach(item => {
    const sliceAngle = (item.value / total) * Math.PI * 2;

    ctx.fillStyle = item.color;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
    ctx.arc(centerX, centerY, innerRadius, currentAngle + sliceAngle, currentAngle, true);
    ctx.closePath();
    ctx.fill();

    currentAngle += sliceAngle;
  });
}

function initTarifForm() {
  const form = $('#tarifForm');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    showToast('Tarif mis à jour avec succès !');
  });
}

// ============================================
// LOGOUT
// ============================================

function initLogout() {
  const logoutBtn = $('#logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      currentUser = null;
      localStorage.removeItem('currentUser');
      window.location.href = 'index.html';
    });
  }
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  // Initialize mobile menu
  initMobileMenu();

  // Initialize page-specific functions
  initLogin();
  initRegister();
  initLogout();

  // Initialize dashboards based on page
  if (document.body.classList.contains('page-client')) {
    initClientDashboard();
  }

  if (document.body.classList.contains('page-gardien')) {
    initGardienDashboard();
  }

  if (document.body.classList.contains('page-admin')) {
    initAdminDashboard();

    // Redraw charts on window resize
    window.addEventListener('resize', () => {
      renderRevenueChart();
      renderOccupancyChart();
    });
  }
});