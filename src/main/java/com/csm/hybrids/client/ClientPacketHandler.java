package com.csm.hybrids.client;

import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.network.AnimSpec;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.world.entity.Entity;

public final class ClientPacketHandler {

    public static void handleSync(int entityId, HybridData.SyncState state) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) {
            return;
        }
        Entity entity = mc.level.getEntity(entityId);
        if (!(entity instanceof AbstractClientPlayer player)) {
            return;
        }
        HybridData data = HybridCapability.get(player);
        ClientHybridState st = ClientHybridState.of(player);
        if (data == null || st == null) {
            return;
        }
        HybridType oldType = data.type();
        boolean wasTransformed = data.isTransformed();
        data.applySync(state);
        if (data.type().monster()) {
            st.type = data.type();
            st.puppet(player); // exists before the manifest animation is triggered on it
        }
        st.onSync(oldType, wasTransformed, data);
        if (wasTransformed != data.isTransformed() || oldType != data.type()) {
            player.refreshDimensions(); // a devil's form is bigger than a person
        }
    }

    public static void handleAnim(int entityId, AnimSpec spec) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) {
            return;
        }
        Entity entity = mc.level.getEntity(entityId);
        if (entity instanceof AbstractClientPlayer player) {
            ClientHybridState st = ClientHybridState.of(player);
            if (st != null) {
                st.onAnim(spec, player);
            }
        }
    }

    private ClientPacketHandler() {
    }
}
