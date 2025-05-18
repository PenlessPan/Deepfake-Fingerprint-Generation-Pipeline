# Deepfake Fingerprint Generation Pipeline

This repository contains an open-source implementation of an end-to-end **deepfake fingerprint generation pipeline**. It allows researchers to generate synthetic (spoofed) fingerprint images from stolen minutiae templates and materialize them as physical silicone replicas for evaluating real-world biometric spoofing attacks.

> 📢 This work was published at **WDC '25 – The 4th Workshop on Security Implications of Deepfakes and Cheapfakes**.  
> Authors: Yaniv Hacmon, Keren Gorelik, Yisroel Mirsky

---

## 💡 Overview

Biometric templates, particularly fingerprint minutiae maps, are often considered safe due to their abstract format. This repository challenges that assumption by providing:

- A **Pix2Pix-based GAN model** to generate fingerprint images from minutiae-based template images.
- A **template-to-image renderer** to convert ISO/IEC-style minutiae templates into RGB visual representations.
- A **3D mold generator** to convert 2D fingerprint images into STL models for silicone mold casting.
- Scripts to **train, evaluate, and visualize** the synthetic fingerprints.
- Guidelines for **fabricating physical spoofs** and replicating the attack in the lab.

---

## 🧪 Use Cases

- Research in biometric spoofing and anti-spoofing defenses.
- Security audits for fingerprint-based authentication systems.
- Development of robust biometric template encryption or cancelable biometrics.
- Educational demonstrations of biometric vulnerabilities.

---

