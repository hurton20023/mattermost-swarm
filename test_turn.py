import asyncio
import logging
from aiortc import RTCPeerConnection, RTCIceServer, RTCConfiguration

# --- CONFIGURATION (Must match docker-stack.yml) ---
TURN_URL  = "turn:192.168.1.154:3478?transport=udp"
TURN_USER = "mmuser"
TURN_PASS = "mmuser_turn_password_change_me"
# --------------------------------------------------

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

    print(f"--- Attempting to find TURN Relay Candidate on: {TURN_URL} ---")

    try:
        # Create an offer to start ICE gathering
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        found_relay = False
        print("Gathering candidates...")
        
        # Wait up to 15 seconds
        for i in range(15):
            sdp = pc.localDescription.sdp
            for line in sdp.split('\n'):
                if 'typ relay' in line:
                    print(f"\n✅ SUCCESS! TURN relay candidate found:\n   {line.strip()}")
                    found_relay = True
                    break
            if found_relay:
                break
            await asyncio.sleep(1)

        if not found_relay:
            print("\n❌ FAILED: No relay candidate found.")
            print("Check CoTURN logs for 'Unauthorized' or 'Wrong credentials' errors.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    finally:
        await pc.close()

if __name__ == "__main__":
    # We turn up the logging for aioice to see exactly what's failing
    # This will help us see the raw STUN messages if it fails
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_turn())
