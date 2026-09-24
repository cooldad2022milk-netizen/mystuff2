package com.csm.hybrids.command;

import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridLogic;
import com.csm.hybrids.hybrid.HybridType;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.FloatArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

import java.util.Arrays;

/**
 * /csm hybrid <player> <none|any hybrid or fiend id>
 * /csm blood <player> <amount>
 * /csm transform <player>
 */
public final class CsmCommand {
    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Commands.literal("csm").requires(s -> s.hasPermission(2))
                .then(Commands.literal("hybrid").then(Commands.argument("player", EntityArgument.player())
                        .then(Commands.argument("type", StringArgumentType.word())
                                .suggests((c, b) -> SharedSuggestionProvider.suggest(
                                        Arrays.stream(HybridType.values()).map(t -> t.id), b))
                                .executes(CsmCommand::setHybrid))))
                .then(Commands.literal("blood").then(Commands.argument("player", EntityArgument.player())
                        .then(Commands.argument("amount", FloatArgumentType.floatArg(0, HybridData.MAX_BLOOD))
                                .executes(CsmCommand::setBlood))))
                .then(Commands.literal("transform").then(Commands.argument("player", EntityArgument.player())
                        .executes(CsmCommand::toggleForm))));
    }

    private static int setHybrid(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        ServerPlayer player = EntityArgument.getPlayer(ctx, "player");
        HybridType type = HybridType.byId(StringArgumentType.getString(ctx, "type"));
        HybridData data = HybridCapability.get(player);
        if (data == null) {
            return 0;
        }
        HybridLogic.setType(player, data, type);
        ctx.getSource().sendSuccess(() -> Component.translatable("commands.csm.hybrid", player.getDisplayName(), type.displayName()), true);
        return 1;
    }

    private static int setBlood(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        ServerPlayer player = EntityArgument.getPlayer(ctx, "player");
        float amount = FloatArgumentType.getFloat(ctx, "amount");
        HybridData data = HybridCapability.get(player);
        if (data == null) {
            return 0;
        }
        data.setBlood(amount);
        HybridLogic.sync(player, data);
        ctx.getSource().sendSuccess(() -> Component.translatable("commands.csm.blood", player.getDisplayName(), (int) amount), true);
        return 1;
    }

    private static int toggleForm(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        ServerPlayer player = EntityArgument.getPlayer(ctx, "player");
        HybridData data = HybridCapability.get(player);
        if (data == null || !data.isHybrid()) {
            return 0;
        }
        HybridLogic.tryUseAbility(player, 0);
        return 1;
    }

    private CsmCommand() {
    }
}
