import asyncio
import logging
from aiortc import RTCPeerConnection, RTCIceServer, RTCConfiguration

# --- CONFIGURATION ---
TURN_URL = "turn:192.168.1.154:3478"
TURN_USER = "mmuser"
TURN_PASS = "mmuser_turn_password_change_me"
# ---------------------

async def test_turn():
    # Setup the ICE Server configuration
    ice_servers = [
        RTCIceServer(
            urls=[TURN_URL],
            username=TURN_USER,
            credential=TURN_PASS
        )
    ]
    config = RTCConfiguration(iceServers=ice_servers)
    pc = RTCPeerConnection(configuration=config)

    # We need to create a data channel to trigger ICE gathering
    pc.createDataChannel("test-channel")

    print(f"--- Testing TURN Server: {TURN_URL} ---")
    print("Gathering ICE candidates... (Wait ~10 seconds)")

    try:
        # Create an offer to start ICE gathering
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        # Wait for gathering to complete or find a 'relay' candidate
        found_relay = False
        for i in range(20): # Timeout after 20 seconds
            for candidate in pc.localDescription.sdp.split('\n'):
                if 'typ relay' in candidate:
                    print(f"\n✅ SUCCESS! Found Relay Candidate: {candidate.strip()}")
                    found_relay = True
                    break
            if found_relay:
                break
            await asyncio.sleep(1)

        if not found_relay:
            print("\n❌ FAILED: No 'relay' candidates found. Your TURN server is not reachable or auth failed.")
            print("Check your firewall (UDP 3478) and CoTURN logs.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    finally:
        await pc.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    asyncio.run(test_turn())
