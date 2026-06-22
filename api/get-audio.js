const { S3Client, GetObjectCommand } = require("@aws-sdk/client-s3");
const { getSignedUrl } = require("@aws-sdk/s3-request-presigner");

module.exports = async (req, res) => {
  // CORS Headers
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  const { track, password, book } = req.query;

  // 1. Verify Password
  const correctPassword = process.env.ACCESS_PASSWORD || "AS-CAPITAL-2026";
  if (!password || password.trim().toUpperCase() !== correctPassword) {
    return res.status(403).json({ error: "Contraseña incorrecta de acceso." });
  }

  // 2. Verify Track Parameter
  if (!track) {
    return res.status(400).json({ error: "Parámetro track requerido." });
  }

  // Determine key prefix / folder based on book
  let folder = "capital";
  if (book === "cpm") {
    folder = "cpm";
  }

  // Target Key in S3
  const fileKey = `${folder}/${track}`;

  try {
    // 3. Configure S3 Client (compatible with AWS, R2, B2)
    const s3Client = new S3Client({
      region: process.env.S3_REGION || "auto",
      endpoint: process.env.S3_ENDPOINT, // e.g. https://<id>.r2.cloudflarestorage.com
      credentials: {
        accessKeyId: process.env.S3_ACCESS_KEY_ID,
        secretAccessKey: process.env.S3_SECRET_ACCESS_KEY,
      },
    });

    // 4. Create GetObject Command
    const command = new GetObjectCommand({
      Bucket: process.env.S3_BUCKET_NAME,
      Key: fileKey,
    });

    // 5. Generate Signed URL (valid for 5 minutes / 300 seconds)
    const signedUrl = await getSignedUrl(s3Client, command, { expiresIn: 300 });

    return res.status(200).json({ url: signedUrl });
  } catch (error) {
    console.error("Error generating signed URL:", error);
    return res.status(500).json({ error: "Error al generar enlace seguro: " + error.message });
  }
};
