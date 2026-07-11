// ===============================
// Portfolio Loaded Message
// ===============================
console.log("Portfolio Website Loaded Successfully!");


// ===============================
// Navbar Active Link on Scroll
// ===============================
const sections = document.querySelectorAll("section");
const navLinks = document.querySelectorAll(".nav-links a");

window.addEventListener("scroll", () => {
    let current = "";

    sections.forEach(section => {
        const sectionTop = section.offsetTop - 100;

        if (pageYOffset >= sectionTop) {
            current = section.getAttribute("id");
        }
    });

    navLinks.forEach(link => {
        link.classList.remove("active");

        if (link.getAttribute("href").includes(current)) {
            link.classList.add("active");
        }
    });
});


// ===============================
// Theme Toggle (Dark / Light)
// ===============================
const themeToggle = document.querySelector(".theme-toggle");

if (themeToggle) {
    themeToggle.addEventListener("click", () => {
        const root = document.documentElement;
        const isDark = root.getAttribute("data-theme") === "dark";

        root.setAttribute("data-theme", isDark ? "light" : "dark");
        themeToggle.textContent = isDark ? "🌙" : "☀️";
    });
}


// ===============================
// EmailJS Init
// ===============================
(function () {
    try {
        if (typeof emailjs === "undefined") {
            console.error("EmailJS SDK not found. Ensure the CDN script is loaded before script.js");
            return;
        }

        // EmailJS docs show string init: emailjs.init('YOUR_PUBLIC_KEY')
        try {
            emailjs.init("vdhj7hxig1Tf_Fd-l");
        } catch (err) {
            // fallback to object form if needed
            emailjs.init({ publicKey: "vdhj7hxig1Tf_Fd-l" });
        }

        console.log("EmailJS initialized (public key set)");
    } catch (err) {
        console.error("EmailJS initialization error:", err);
    }
})();


// ===============================
// Contact Form
// ===============================
const contactForm = document.getElementById("contact-form");
const formSuccess = document.getElementById("form-success");

if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
        e.preventDefault();

        console.log("Form submitted");

        const submitBtn = contactForm.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;

        // explicit form reference (avoid relying on `this`)
        emailjs.sendForm("service_r4r21km", "template_8xfpums", contactForm)
        .then((response) => {
            console.log("EmailJS SUCCESS", response);

            formSuccess.textContent = "✅ Message sent successfully!";
            formSuccess.style.color = "green";
            formSuccess.style.display = "block";

            contactForm.reset();
            if (submitBtn) submitBtn.disabled = false;
        })
        .catch((error) => {
            console.error("EmailJS FAILED", error);

            let msg = "❌ Failed to send message.";
            try {
                if (error && error.text) msg += ` ${error.text}`;
                else if (error && error.status) msg += ` (status: ${error.status})`;
            } catch (e) {}

            formSuccess.textContent = msg;
            formSuccess.style.color = "red";
            formSuccess.style.display = "block";

            // keep debug alert optional but helpful
            try { alert(JSON.stringify(error)); } catch (e) {}

            if (submitBtn) submitBtn.disabled = false;
        });
    });
} else {
    console.warn("Contact form element not found: #contact-form");
}