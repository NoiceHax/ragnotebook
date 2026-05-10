export default async (req) => {
  console.log("Running scheduled ping to keep backend awake...");
  
  // ⚠️ Replace this with your actual Render/Railway backend URL
  const backendUrl = "https://your-backend-app.onrender.com/api/health";
  
  try {
    const response = await fetch(backendUrl);
    console.log(`Backend responded with status: ${response.status}`);
  } catch (error) {
    console.error("Failed to ping backend:", error.message);
  }

  return new Response("Ping complete", { status: 200 });
};

export const config = {
  // Cron expression for every 10 minutes
  schedule: "*/10 * * * *"
};
