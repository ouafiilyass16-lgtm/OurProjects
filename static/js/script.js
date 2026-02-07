/**
 * Smart Parking Management System
 * Main JavaScript File - Updated for Flask Backend
 */

// ============================================
// UTILITY FUNCTIONS
// ============================================

function $(selector) {
  return document.querySelector(selector);
}

function $$(selector) {
  return document.querySelectorAll(selector);
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
// CLIENT DASHBOARD
// ============================================

function initClientDashboard() {
  initReservationModal();
}

function initReservationModal() {
  const modal = $('#reservationModal');
  const cancelBtn = $('#cancelReservation');
  const confirmBtn = $('#confirmReservation');

  // Les places sont rendues par le serveur, on ajoute les écouteurs sur les boutons existants
  const spots = $$('.parking-spot.free');
  spots.forEach(spot => {
    spot.addEventListener('click', () => {
      const spotId = spot.dataset.spotId;
      const spotName = spot.textContent.trim();
      openReservationModal(spotId, spotName);
    });
  });

  if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
      modal.classList.remove('active');
    });
  }

  if (confirmBtn) {
    confirmBtn.addEventListener('click', () => {
      const spotId = confirmBtn.dataset.spotId;
      const matricule = $('#matricule').value;
      const marque = $('#marque').value;
      const couleur = $('#couleur').value;

      if (!matricule) {
        $('#matriculeError').style.display = 'flex';
        return;
      }

      // Créer un formulaire caché pour soumettre en POST
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = '/choisir_place';

      const fields = {
        'place_id': spotId,
        'matricule': matricule,
        'marque': marque,
        'couleur': couleur
      };

      for (const [name, value] of Object.entries(fields)) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = name;
        input.value = value;
        form.appendChild(input);
      }

      document.body.appendChild(form);
      form.submit();
    });
  }
}

function openReservationModal(spotId, spotName) {
  const modal = $('#reservationModal');
  const title = $('#reservationModalTitle');
  const confirmBtn = $('#confirmReservation');

  if (modal && title && confirmBtn) {
    title.innerHTML = `<i data-lucide="car" class="text-green-600" style="width: 20px; height: 20px;"></i> Réserver la place ${spotName}`;
    confirmBtn.dataset.spotId = spotId;
    modal.classList.add('active');
    lucide.createIcons();
  }
}

// ============================================
// LOGOUT
// ============================================

function initLogout() {
  const logoutBtn = $('#logoutBtn');
  const logoutBtnMobile = $('#logoutBtnMobile');

  const handleLogout = () => {
    window.location.href = '/logout';
  };

  if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);
  if (logoutBtnMobile) logoutBtnMobile.addEventListener('click', handleLogout);
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

  // Initialize logout
  initLogout();

  // Initialize dashboards based on page class
  if (document.body.classList.contains('page-client')) {
    initClientDashboard();
  }
});
