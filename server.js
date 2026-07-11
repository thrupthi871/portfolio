const express = require('express');
const cors = require('cors');
const path = require('path');
const nodemailer = require('nodemailer');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname)));

app.post('/api/contact', async (req, res) => {
  const { name, email, message } = req.body || {};

  if (!name || !email || !message) {
    return res.status(400).json({ success: false, message: 'Please fill in all fields.' });
  }

  const gmailUser = process.env.GMAIL_USER;
  const gmailPassword = process.env.GMAIL_APP_PASSWORD;
  const recipient = process.env.CONTACT_EMAIL || gmailUser;

  if (!gmailUser || !gmailPassword) {
    return res.status(500).json({
      success: false,
      message: 'Email sending is not configured yet. Please add your Gmail credentials.'
    });
  }

  try {
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: gmailUser,
        pass: gmailPassword
      }
    });

    await transporter.sendMail({
      from: `Portfolio Contact <${gmailUser}>`,
      to: recipient,
      replyTo: email,
      subject: `New message from ${name}`,
      text: `Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`
    });

    res.json({ success: true, message: 'Message sent successfully.' });
  } catch (error) {
    console.error(error);
    res.status(500).json({ success: false, message: 'Failed to send message. Please try again later.' });
  }
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
