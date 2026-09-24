package com.csm.hybrids.network;

import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridLogic;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Ability wheel selection. */
public record SelectAbilityPacket(int index) {
    public static void encode(SelectAbilityPacket msg, FriendlyByteBuf buf) {
        buf.writeByte(msg.index);
    }

    public static SelectAbilityPacket decode(FriendlyByteBuf buf) {
        return new SelectAbilityPacket(buf.readByte());
    }

    public static void handle(SelectAbilityPacket msg, Supplier<NetworkEvent.Context> ctx) {
        ServerPlayer player = ctx.get().getSender();
        if (player != null) {
            HybridData data = HybridCapability.get(player);
            if (data != null && data.hasAbilities()) {
                data.setSelected(msg.index);
                HybridLogic.sync(player, data);
            }
        }
        ctx.get().setPacketHandled(true);
    }
}
