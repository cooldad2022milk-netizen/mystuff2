package com.csm.hybrids.network;

import com.csm.hybrids.hybrid.HybridLogic;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Client asks to perform ability {@code index} of its hybrid (index 0 is always the trigger). */
public record UseAbilityPacket(int index) {
    public static void encode(UseAbilityPacket msg, FriendlyByteBuf buf) {
        buf.writeByte(msg.index);
    }

    public static UseAbilityPacket decode(FriendlyByteBuf buf) {
        return new UseAbilityPacket(buf.readByte());
    }

    public static void handle(UseAbilityPacket msg, Supplier<NetworkEvent.Context> ctx) {
        ServerPlayer player = ctx.get().getSender();
        if (player != null) {
            HybridLogic.tryUseAbility(player, msg.index);
        }
        ctx.get().setPacketHandled(true);
    }
}
