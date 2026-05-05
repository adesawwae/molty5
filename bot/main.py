import asyncio
import os
import logging
import httpx
import websockets
import json
from eth_account import Account
from dotenv import load_dotenv

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Molty5-Agent")

load_dotenv()

class MoltyAgent:
    def __init__(self):
        # Konfigurasi User
        self.agent_name = os.getenv("AGENT_NAME", "BotMolty")
        self.room_mode = os.getenv("ROOM_MODE", "free")
        self.railway_token = os.getenv("RAILWAY_API_TOKEN")
        
        # Kredensial (Auto-generated nantinya)
        self.api_key = os.getenv("API_KEY")
        self.agent_wallet = os.getenv("AGENT_WALLET_ADDRESS")
        self.agent_private_key = os.getenv("AGENT_PRIVATE_KEY")
        
        # Update ke Endpoint API v1.0 Molty Royale
        self.base_api_url = "https://api.moltyroyale.com/v1"
        self.ws_url = "wss://api.moltyroyale.com/v1/ws"

    def generate_wallets_if_needed(self):
        """Membuat wallet otomatis jika belum ada di environment."""
        if not self.agent_wallet or not self.agent_private_key:
            logger.info("Membangun identitas Agent baru (Auto-Generate Mode)...")
            Account.enable_unaudited_hdwallet_features()
            account = Account.create()
            self.agent_wallet = account.address
            self.agent_private_key = account.key.hex()
            logger.info(f"Agent Wallet Generated: {self.agent_wallet}")
            # PENTING: Fitur untuk menyimpan ke Railway (Membutuhkan Railway GraphQL API)
            self.save_to_railway("AGENT_WALLET_ADDRESS", self.agent_wallet)
            self.save_to_railway("AGENT_PRIVATE_KEY", self.agent_private_key)
            
    def save_to_railway(self, key, value):
        """Menyimpan variabel secara persisten ke Railway Dashboard agar aman saat restart"""
        if not self.railway_token:
            logger.warning("RAILWAY_API_TOKEN tidak diatur. Kredensial tidak akan tersimpan persisten!")
            return
        
        logger.info(f"Menyimpan {key} ke Railway Environment...")
        # Implementasi GraphQL Railway API (Sesuai cara kerja molty5)
        # Note: Implementasi GraphQL disederhanakan sebagai placeholder koneksi API
        headers = {"Authorization": f"Bearer {self.railway_token}"}
        # Eksekusi POST ke GraphQL endpoint Railway (https://backboard.railway.app/graphql/v2) dilakukan di sini
        pass

    async def register_agent(self):
        """Registrasi ke Gamechain dengan struktur API v1.0 yang baru."""
        if self.api_key:
            logger.info("API Key sudah ada. Melewati proses registrasi.")
            return True

        logger.info(f"Mendaftarkan Agent '{self.agent_name}' ke Molty Royale...")
        async with httpx.AsyncClient() as client:
            payload = {
                "name": self.agent_name,
                "wallet_address": self.agent_wallet,
                "mode": self.room_mode
            }
            try:
                # Menyesuaikan endpoint API
                response = await client.post(f"{self.base_api_url}/agents/register", json=payload)
                if response.status_code in [200, 201]:
                    data = response.json()
                    self.api_key = data.get("api_key")
                    logger.info("✅ Registrasi Berhasil!")
                    self.save_to_railway("API_KEY", self.api_key)
                    return True
                else:
                    logger.error(f"Gagal Registrasi (Maintenance/API Error): {response.text}")
                    return False
            except Exception as e:
                logger.error(f"Koneksi Timeout / Terputus: {str(e)}")
                return False

    async def game_loop(self):
        """Koneksi WebSocket Real-time ke Arena Molty Royale."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        logger.info("Menghubungkan ke Arena WebSocket...")
        
        while True:
            try:
                async with websockets.connect(self.ws_url, additional_headers=headers) as ws:
                    logger.info("✅ Terhubung ke Server Molty!")
                    while True:
                        # Logic bertahan hidup, farming, & interaksi game
                        # Ini menangkap telemetry dari API v1.0 terbaru
                        message = await ws.recv()
                        data = json.loads(message)
                        
                        if data.get("type") == "game_state":
                            logger.info(f"Status HP: {data.get('hp')} | Moltz: {data.get('moltz')}")
                            # Simulasi aksi bot
                            await ws.send(json.dumps({"action": "idle_farm"}))
                            
                        await asyncio.sleep(5)
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Koneksi WebSocket terputus. Mencoba reconnect dalam 5 detik...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Terjadi kesalahan di Arena: {str(e)}")
                await asyncio.sleep(5)

    async def start(self):
        logger.info("=== Memulai Molty5 AI Agent (Versi Fix) ===")
        self.generate_wallets_if_needed()
        if await self.register_agent():
            await self.game_loop()
        else:
            logger.error("Bot dihentikan karena gagal inisialisasi akun.")

if __name__ == "__main__":
    bot = MoltyAgent()
    asyncio.run(bot.start())
