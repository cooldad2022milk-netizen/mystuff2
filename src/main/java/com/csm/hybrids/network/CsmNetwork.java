package com.csm.hybrids.network;

import com.csm.hybrids.CsmMod;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

public final class CsmNetwork {
    private static final String PROTOCOL = "2";
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(CsmMod.id("main"),
            () -> PROTOCOL, PROTOCOL::equals, PROTOCOL::equals);

    public static void register() {
        int id = 0;
        CHANNEL.messageBuilder(UseAbilityPacket.class, id++, NetworkDirection.PLAY_TO_SERVER)
                .encoder(UseAbilityPacket::encode).decoder(UseAbilityPacket::decode)
                .consumerMainThread(UseAbilityPacket::handle).add();
        CHANNEL.messageBuilder(SelectAbilityPacket.class, id++, NetworkDirection.PLAY_TO_SERVER)
                .encoder(SelectAbilityPacket::encode).decoder(SelectAbilityPacket::decode)
                .consumerMainThread(SelectAbilityPacket::handle).add();
        CHANNEL.messageBuilder(SyncHybridPacket.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(SyncHybridPacket::encode).decoder(SyncHybridPacket::decode)
                .consumerMainThread(SyncHybridPacket::handle).add();
        CHANNEL.messageBuilder(PlayAnimPacket.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(PlayAnimPacket::encode).decoder(PlayAnimPacket::decode)
                .consumerMainThread(PlayAnimPacket::handle).add();
    }

    public static void toServer(Object msg) {
        CHANNEL.sendToServer(msg);
    }

    public static void toPlayer(ServerPlayer player, Object msg) {
        CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), msg);
    }

    public static void toTracking(Entity entity, Object msg) {
        CHANNEL.send(PacketDistributor.TRACKING_ENTITY.with(() -> entity), msg);
    }

    public static void toTrackingAndSelf(Entity entity, Object msg) {
        CHANNEL.send(PacketDistributor.TRACKING_ENTITY_AND_SELF.with(() -> entity), msg);
    }

    private CsmNetwork() {
    }
}
