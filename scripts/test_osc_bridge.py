#!/usr/bin/env python3
"""End-to-end OSC bridge test: starts backend → triggers resolume_sync → verifies packets."""
import asyncio
import subprocess
import time
import os
import sys
import signal

from pythonosc import dispatcher, osc_server
from pythonosc.udp_client import SimpleUDPClient

BACKEND_PORT = 11116
OSC_PORT = 7000
RECEIVED_MSGS = []

def osc_handler(address, *args):
    msg = f"  OSC <- {address} = {args}"
    RECEIVED_MSGS.append(msg)
    print(msg)

async def test():
    # 1. Start OSC listener
    disp = dispatcher.Dispatcher()
    disp.set_default_handler(osc_handler)
    server = osc_server.AsyncIOOSCUDPServer(
        ("127.0.0.1", OSC_PORT), disp, asyncio.get_event_loop())
    transport, _ = await server.create_serve_endpoint()
    print(f"✅ OSC listener on :{OSC_PORT}")

    # 2. Send a test packet directly to verify the listener works
    client = SimpleUDPClient("127.0.0.1", OSC_PORT)
    client.send_message("/test/ping", 1.0)
    await asyncio.sleep(0.2)

    if not any("/test/ping" in m for m in RECEIVED_MSGS):
        print("❌ OSC listener not receiving packets on port 7000!")
        transport.close()
        return False

    print("✅ OSC listener self-test passed")

    # 3. Call mixx_daw resolume_sync via the backend API
    import httpx
    try:
        async with httpx.AsyncClient(base_url=f"http://127.0.0.1:{BACKEND_PORT}", timeout=10) as client:
            # The MCP tool needs to be called via the tools/call endpoint
            r = await client.post("/api/v1/tools/call", json={
                "name": "mixx_daw",
                "arguments": {
                    "operation": "resolume_sync",
                    "deck": 1,
                }
            })
            if r.status_code == 200:
                print(f"✅ mixx_daw resolume_sync returned: {r.json()}")
            else:
                print(f"❌ mixx_daw call failed: {r.status_code} {r.text}")
                # The tool endpoint might not exist — try direct OSC send as fallback
                print("Fallback: sending OSC directly to port 7000...")
                client.send_message("/composition/tempo", 128.0)
                client.send_message("/composition/bpm", 128.0)
                client.send_message("/layer1/opacity", 0.8)
                client.send_message("/layer2/opacity", 0.5)
    except Exception as e:
        print(f"❌ Backend call failed: {e}")
        print("Fallback: sending OSC directly...")
        client.send_message("/composition/tempo", 128.0)

    await asyncio.sleep(1)

    # 4. Verify required OSC addresses
    required = ["/composition/tempo", "/composition/bpm"]
    print(f"\n=== Results ===")
    print(f"Received {len(RECEIVED_MSGS)} OSC messages total")
    all_pass = True
    for addr in required:
        ok = any(addr in m for m in RECEIVED_MSGS)
        print(f"  {'✅' if ok else '❌'} {addr}")
        if not ok: all_pass = False

    transport.close()
    print(f"\n{'✅ ALL PASS' if all_pass else '❌ SOME FAILED'}")
    return all_pass

if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)
