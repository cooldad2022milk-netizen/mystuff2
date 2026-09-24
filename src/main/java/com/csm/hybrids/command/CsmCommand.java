package com.csm.hybrids.command;

import com.csm.hybrids.contract.Contract;
import com.csm.hybrids.contract.Contracts;
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
 * /csm hybrid <player> <none|any hybrid, fiend or devil id>
 * /csm contract <player> add|remove <fox_head|fox_paw|curse|future|ghost>
 * /csm contract <player> list
 * /csm blood <player> <amount>
 * /csm transform <player>
 */
public final class CsmCommand {
    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Commands.literal("csm").requires(s -> s.hasPermission(2))
                .then(Commands.literal("hybrid").then(Commands.argument("player", EntityArgument.player())
                        .then(Commands.argument("type", StringArgumentType.word())
                                .suggests((c, b) -> SharedSuggestionProvider.suggest(
                                        Arrays.stream(HybridType.values()).filter(HybridType::playable).map(t -> t.id), b))
                                .executes(CsmCommand::setHybrid))))
                .then(Commands.literal("contract").then(Commands.argument("player", EntityArgument.player())
                        .then(Commands.literal("add").then(Commands.argument("contract", StringArgumentType.word())
                                .suggests((c, b) -> SharedSuggestionProvider.suggest(
                                        Arrays.stream(Contract.values()).map(k -> k.id), b))
                                .executes(c -> contract(c, true))))
                        .then(Commands.literal("remove").then(Commands.argument("contract", StringArgumentType.word())
                                .suggests((c, b) -> SharedSuggestionProvider.suggest(
                                        Arrays.stream(Contract.values()).map(k -> k.id), b))
                                .executes(c -> contract(c, false))))
                        .then(Commands.literal("list").executes(CsmCommand::listContracts))))
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
        if (!type.playable()) {
            ctx.getSource().sendFailure(Component.translatable("commands.csm.not_playable", type.displayName()));
            return 0;
        }
        HybridLogic.setType(player, data, type);
        ctx.getSource().sendSuccess(() -> Component.translatable("commands.csm.hybrid", player.getDisplayName(), type.displayName()), true);
        return 1;
    }

    private static int contract(CommandContext<CommandSourceStack> ctx, boolean add) throws CommandSyntaxException {
        ServerPlayer player = EntityArgument.getPlayer(ctx, "player");
        String id = StringArgumentType.getString(ctx, "contract");
        Contract c = Contract.byId(id);
        HybridData data = HybridCapability.get(player);
        if (c == null) {
            ctx.getSource().sendFailure(Component.translatable("commands.csm.contract_unknown", id));
            return 0;
        }
        if (data == null) {
            return 0;
        }
        boolean changed = add ? Contracts.sign(player, data, c) : Contracts.breakContract(player, data, c);
        if (!changed) {
            ctx.getSource().sendFailure(Component.translatable(add ? "commands.csm.contract_has" : "commands.csm.contract_hasnt",
                    player.getDisplayName(), c.displayName()));
            return 0;
        }
        ctx.getSource().sendSuccess(() -> Component.translatable(add ? "commands.csm.contract_add" : "commands.csm.contract_remove",
                player.getDisplayName(), c.displayName()), true);
        return 1;
    }

    private static int listContracts(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        ServerPlayer player = EntityArgument.getPlayer(ctx, "player");
        HybridData data = HybridCapability.get(player);
        if (data == null) {
            return 0;
        }
        StringBuilder names = new StringBuilder();
        for (Contract c : data.contracts()) {
            if (names.length() > 0) {
                names.append(", ");
            }
            names.append(c.displayName().getString());
        }
        String list = names.toString();
        ctx.getSource().sendSuccess(() -> Component.translatable("commands.csm.contract_list", player.getDisplayName(),
                list.isEmpty() ? "-" : list, data.curseToll()), false);
        return data.contracts().size();
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
