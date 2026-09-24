package com.csm.hybrids.dev;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.devil.DevilAbility;
import com.csm.hybrids.contract.Contract;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridLogic;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.item.ContractItem;
import com.csm.hybrids.registry.ModEntities;
import com.csm.hybrids.registry.ModItems;
import com.csm.hybrids.util.Safe;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.Husk;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.common.util.FakePlayerFactory;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.UUID;
import java.util.function.Consumer;

/**
 * Headless smoke test, only active with {@code -Dcsm.smoketest=true} (CI: {@code gradlew runServer -PcsmSmoke}).
 * <p>
 * On a dedicated server, fake players become every hybrid, fiend and devil and use every move, sign every contract
 * and call up every contract devil, and every devil mob is spawned and made to use each of its moves - all at once,
 * in lanes side by side. Anything that throws is logged as {@code [smoke] FAIL}; the run ends with
 * {@code [smoke] DONE ... failures=N} and the server stops. A crash takes the server down with a crash report.
 */
@Mod.EventBusSubscriber(modid = CsmMod.MODID)
public final class SmokeTest {
    private static final boolean ENABLED = Boolean.getBoolean("csm.smoketest");
    /** Give up (and fail) after this long. */
    private static final int TIMEOUT = 20 * 60 * 30;
    private static final int PLAYER_LANES = 6;
    private static final int DEVIL_LANES = 4;

    private static final List<Lane> LANES = new ArrayList<>();
    private static final List<String> FAILED = new ArrayList<>();
    private static int steps;
    private static int skipped;
    private static int ticks;
    private static boolean done;

    private record Step(String what, int waitAfter, Consumer<Lane> action) {
    }

    private static final class Lane {
        final String name;
        final Vec3 origin;
        final Deque<Step> queue = new ArrayDeque<>();
        FakePlayer player;
        int wait = 20;

        Lane(String name, Vec3 origin) {
            this.name = name;
            this.origin = origin;
        }

        void add(String what, int waitAfter, Consumer<Lane> action) {
            queue.addLast(new Step(what, waitAfter, action));
        }

        /** Run these next, before anything already queued. */
        void next(List<Step> steps) {
            for (int i = steps.size() - 1; i >= 0; i--) {
                queue.addFirst(steps.get(i));
            }
        }

        ServerLevel level() {
            return (ServerLevel) player.level();
        }

        HybridData data() {
            return HybridCapability.get(player);
        }
    }

    // ------------------------------------------------------------------ driver
    @SubscribeEvent
    public static void started(ServerStartedEvent event) {
        if (!ENABLED) {
            return;
        }
        MinecraftServer server = event.getServer();
        ServerLevel level = server.overworld();
        BlockPos spawn = level.getSharedSpawnPos();
        List<HybridType> playable = new ArrayList<>();
        List<HybridType> devils = new ArrayList<>();
        for (HybridType t : HybridType.values()) {
            if (t != HybridType.NONE && t.playable()) {
                playable.add(t);
            }
            if (t.devil) {
                devils.add(t);
            }
        }
        int n = PLAYER_LANES + DEVIL_LANES + 1;
        for (int i = 0; i < n; i++) {
            int x = spawn.getX() + (i % 6) * 24 - 60;
            int z = spawn.getZ() + (i / 6) * 40 - 20;
            // entities only keep ticking on a server nobody is on inside forced chunks
            for (int dx = -2; dx <= 2; dx++) {
                for (int dz = -2; dz <= 2; dz++) {
                    level.setChunkForced((x >> 4) + dx, (z >> 4) + dz, true);
                }
            }
            int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z);
            String name = i < PLAYER_LANES ? "player" + i : i < PLAYER_LANES + DEVIL_LANES ? "devil" + (i - PLAYER_LANES)
                    : "contracts";
            Lane lane = new Lane(name, new Vec3(x + 0.5, y, z + 0.5));
            GameProfile profile = new GameProfile(UUID.nameUUIDFromBytes(("csm_smoke_" + name).getBytes(StandardCharsets.UTF_8)),
                    "csm_smoke_" + name);
            lane.player = FakePlayerFactory.get(level, profile);
            resetPlayer(lane);
            LANES.add(lane);
        }
        for (int i = 0; i < playable.size(); i++) {
            hybridSteps(LANES.get(i % PLAYER_LANES), playable.get(i));
        }
        for (int i = 0; i < devils.size(); i++) {
            devilSteps(LANES.get(PLAYER_LANES + i % DEVIL_LANES), devils.get(i));
        }
        contractSteps(LANES.get(n - 1));
        CsmMod.LOGGER.info("[smoke] started: {} hybrids/devils to play, {} devil mobs, {} contracts, {} lanes",
                playable.size(), devils.size(), Contract.values().length, LANES.size());
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (!ENABLED || done || event.phase != TickEvent.Phase.END || LANES.isEmpty()) {
            return;
        }
        ticks++;
        boolean busy = false;
        for (Lane lane : LANES) {
            // fake players are not ticked by the world: run the hybrid rules for them here
            try {
                HybridLogic.tick(lane.player);
            } catch (RuntimeException | LinkageError e) {
                fail(lane, "hybrid tick (" + lane.data().type().id + ")", e);
                lane.data().activeRun = null;
            }
            if (lane.wait > 0) {
                lane.wait--;
                busy = true;
                continue;
            }
            Step step = lane.queue.pollFirst();
            if (step == null) {
                continue;
            }
            busy = true;
            steps++;
            try {
                step.action.accept(lane);
            } catch (RuntimeException | LinkageError e) {
                fail(lane, step.what, e);
            }
            lane.wait = step.waitAfter;
        }
        if (!busy || ticks > TIMEOUT) {
            if (ticks > TIMEOUT) {
                FAILED.add("timed out");
            }
            finish(event.getServer());
        }
    }

    private static void finish(MinecraftServer server) {
        done = true;
        int guarded = Safe.errors();
        CsmMod.LOGGER.info("[smoke] DONE after {} ticks: steps={} skipped={} guarded={} failures={}", ticks, steps,
                skipped, guarded, FAILED.size() + guarded);
        for (String f : FAILED) {
            CsmMod.LOGGER.error("[smoke] failed: {}", f);
        }
        for (String f : Safe.reported()) {
            CsmMod.LOGGER.error("[smoke] guarded: {}", f);
        }
        server.halt(false);
    }

    private static void fail(Lane lane, String what, Throwable e) {
        String msg = lane.name + ": " + what + ": " + e;
        FAILED.add(msg);
        CsmMod.LOGGER.error("[smoke] FAIL {}", msg, e);
    }

    private static void skip(Lane lane, String what, String why) {
        skipped++;
        CsmMod.LOGGER.info("[smoke] skip {}: {} ({})", lane.name, what, why);
    }

    // ------------------------------------------------------------------ hybrids
    private static void hybridSteps(Lane lane, HybridType type) {
        lane.add("become " + type.id, 5, l -> {
            resetPlayer(l);
            HybridLogic.setType(l.player, l.data(), type);
            refill(l);
        });
        lane.add("moves of " + type.id, 0, l -> l.next(moveSteps(l, type)));
        lane.add("save/load " + type.id, 0, l -> {
            CompoundTag tag = l.data().save();
            HybridData copy = new HybridData();
            copy.load(tag);
            if (copy.type() != l.data().baseType()) {
                throw new IllegalStateException("saved " + l.data().baseType().id + ", loaded " + copy.type().id);
            }
        });
        lane.add("human again after " + type.id, 5, l -> {
            HybridLogic.revert(l.player, l.data());
            HybridLogic.setType(l.player, l.data(), HybridType.NONE);
            clearArea(l);
        });
    }

    /** Transform (slot 0), every move in turn, then back to human form. */
    private static List<Step> moveSteps(Lane lane, HybridType type) {
        List<Step> out = new ArrayList<>();
        List<Ability> abilities = lane.data().abilities();
        if (abilities.isEmpty()) {
            return out;
        }
        out.add(new Step(type.id + " slot 0 (transform)", type.triggerTicks + 10, l -> {
            refill(l);
            use(l, 0);
        }));
        for (int i = 1; i < abilities.size(); i++) {
            int slot = i;
            Ability a = abilities.get(i);
            double reach = a instanceof DevilAbility d ? Math.max(1.5, Math.min((d.aiMin + d.aiMax) / 2, 8)) : 4;
            out.add(new Step(type.id + " prepare " + a.id, 3, l -> {
                resetPlayer(l);
                refill(l);
                target(l, reach + l.player.getBbWidth() / 2);
            }));
            out.add(new Step(type.id + " slot " + slot + " (" + a.id + ")", a.duration() + 15, l -> use(l, slot)));
            // the Hero of Hell: the devil inside takes over partway through the move - go through its moves too
            out.add(new Step(type.id + " takeover check after " + a.id, 0, l -> {
                if (l.data().inTakeover()) {
                    l.next(takeoverSteps(l.data().type()));
                }
            }));
        }
        out.add(new Step(type.id + " revert", type.revertTicks + 10, l -> {
            if (l.data().isTransformed() && l.data().activeRun == null) {
                l.data().clearCooldowns();
                use(l, 0);
            }
        }));
        return out;
    }

    /** Every move of a takeover form (Pochita's true form), then the hybrid gets its body back. */
    private static List<Step> takeoverSteps(HybridType form) {
        List<Step> out = new ArrayList<>();
        CsmMod.LOGGER.info("[smoke] takeover: {} with {} moves", form.id, form.abilities().size());
        for (int j = 1; j < form.abilities().size(); j++) {
            int s = j;
            Ability fa = form.abilities().get(j);
            double reach = fa instanceof DevilAbility d ? Math.max(1.5, Math.min((d.aiMin + d.aiMax) / 2, 8)) : 3;
            out.add(new Step(form.id + " prepare " + fa.id, 3, x -> {
                if (!x.data().inTakeover()) {
                    throw new IllegalStateException("the " + form.id + " takeover ended early");
                }
                x.data().takeoverTicks = Math.max(x.data().takeoverTicks, 200); // keep it out for the whole test
                refill(x);
                target(x, reach + x.player.getBbWidth() / 2);
            }));
            out.add(new Step(form.id + " slot " + s + " (" + fa.id + ")", fa.duration() + 15, x -> use(x, s)));
        }
        out.add(new Step("end takeover " + form.id, 10, x -> {
            HybridLogic.endTakeover(x.player, x.data());
            if (x.data().inTakeover() || x.data().type() != form.host()) {
                throw new IllegalStateException("still " + x.data().type().id + " after the takeover ended");
            }
        }));
        return out;
    }

    /** Use a slot the way a player would, logging why it didn't start if it didn't. */
    private static void use(Lane l, int slot) {
        HybridData data = l.data();
        if (slot >= data.abilities().size()) {
            skip(l, "slot " + slot, "no such slot");
            return;
        }
        Ability a = data.abilities().get(slot);
        if (data.activeRun != null) {
            HybridLogic.cancelRun(l.player, data);
        }
        data.clearCooldowns();
        String why = a.checkUse(l.player, data);
        if (why != null) {
            skip(l, a.id, why);
            return;
        }
        HybridLogic.tryUseAbility(l.player, slot);
    }

    // ------------------------------------------------------------------ devil mobs
    private static void devilSteps(Lane lane, HybridType type) {
        DevilEntity[] devil = new DevilEntity[1];
        lane.add("spawn " + type.id + " devil", 20, l -> {
            clearArea(l);
            EntityType<DevilEntity> et = ModEntities.devil(type);
            DevilEntity d = et.create(l.level());
            if (d == null) {
                throw new IllegalStateException("could not create " + type.id);
            }
            d.moveTo(l.origin.x - 4, l.origin.y + (d.spec().flying ? 2 : 0), l.origin.z, 0, 0);
            d.finalizeSpawn(l.level(), l.level().getCurrentDifficultyAt(d.blockPosition()), MobSpawnType.COMMAND, null, null);
            d.setPersistenceRequired();
            l.level().addFreshEntity(d);
            devil[0] = d;
        });
        List<DevilAbility> moves = new ArrayList<>();
        for (Ability a : type.abilities()) {
            if (a instanceof DevilAbility d && d.mobUse) {
                moves.add(d);
            }
        }
        for (int i = 0; i < moves.size(); i++) {
            int idx = i;
            DevilAbility m = moves.get(i);
            lane.add(type.id + " devil uses " + m.id, m.duration() + 10, l -> {
                DevilEntity d = devil[0];
                if (d == null || !d.isAlive()) {
                    skip(l, m.id, "the devil is gone");
                    return;
                }
                double reach = Math.max(1.5, Math.min((m.aiMin + m.aiMax) / 2, 8)) + d.getBbWidth() / 2;
                Husk husk = target(l, reach);
                d.moveTo(husk.getX(), d.getY(), husk.getZ() + reach + 0.3, 180, 0);
                d.setDeltaMovement(Vec3.ZERO);
                d.face(husk);
                d.setTarget(husk);
                d.startMove(m, idx, husk);
            });
        }
        lane.add(type.id + " devil fights on its own", 100, l -> {
            DevilEntity d = devil[0];
            if (d != null && d.isAlive()) {
                d.setTarget(target(l, 5));
            }
        });
        lane.add("kill " + type.id + " devil", 20, l -> {
            DevilEntity d = devil[0];
            if (d != null && d.isAlive()) {
                d.hurt(l.level().damageSources().playerAttack(l.player), 5f);
                d.kill();
            }
            devil[0] = null;
        });
        lane.add("clear after " + type.id, 5, SmokeTest::clearArea);
    }

    // ------------------------------------------------------------------ contracts
    private static void contractSteps(Lane lane) {
        for (Contract c : Contract.values()) {
            lane.add("sign " + c.id, 5, l -> {
                resetPlayer(l);
                ItemStack stack = new ItemStack(ModItems.CONTRACTS.get(c).get());
                if (!(stack.getItem() instanceof ContractItem item) || item.contract() != c) {
                    throw new IllegalStateException("the " + c.id + " contract item is wrong: " + stack);
                }
                stack.getItem().finishUsingItem(stack, l.level(), l.player);
                if (!l.data().hasContract(c)) {
                    throw new IllegalStateException("signing " + c.id + " did not give the contract");
                }
            });
        }
        lane.add("contract moves (human)", 0, l -> l.next(contractMoves(l, "human")));
        lane.add("contracts on a hybrid", 5, l -> {
            resetPlayer(l);
            HybridLogic.setType(l.player, l.data(), HybridType.CHAINSAW);
            refill(l);
        });
        lane.add("contract moves (hybrid)", 0, l -> l.next(contractMoves(l, "chainsaw")));
        lane.add("save/load contracts", 0, l -> {
            HybridData copy = new HybridData();
            copy.load(l.data().save());
            if (copy.contractMask() != l.data().contractMask()) {
                throw new IllegalStateException("contracts lost on save/load");
            }
        });
        for (Contract c : Contract.values()) {
            lane.add("break " + c.id, 1, l -> {
                if (!com.csm.hybrids.contract.Contracts.breakContract(l.player, l.data(), c)) {
                    throw new IllegalStateException("could not break " + c.id);
                }
            });
        }
        lane.add("human again", 5, l -> {
            HybridLogic.setType(l.player, l.data(), HybridType.NONE);
            clearArea(l);
        });
    }

    private static List<Step> contractMoves(Lane lane, String who) {
        List<Step> out = new ArrayList<>();
        List<Ability> abilities = lane.data().abilities();
        for (int i = 0; i < abilities.size(); i++) {
            if (!(abilities.get(i) instanceof com.csm.hybrids.contract.ContractAbility a)) {
                continue;
            }
            int slot = i;
            out.add(new Step(who + " prepare " + a.id, 3, l -> {
                resetPlayer(l);
                refill(l);
                target(l, 4);
                if (a.contract == Contract.HELL) {
                    // the Hell Devil takes its price in lives from around the contractor
                    for (int k = 0; k < com.csm.hybrids.contract.Contracts.HELL_PRICE + 3; k++) {
                        Entity e = EntityType.CHICKEN.create(l.level());
                        if (e != null) {
                            e.moveTo(l.origin.x - 3 + k, l.origin.y, l.origin.z + 3, 0, 0);
                            l.level().addFreshEntity(e);
                        }
                    }
                }
            }));
            // contract devils outlive the move itself (the Hell Devil's hand takes ~3 s to drag its catch under)
            out.add(new Step(who + " " + a.id + " (" + a.contract.id + ")", a.duration() + 70, l -> use(l, slot)));
        }
        return out;
    }

    // ------------------------------------------------------------------ helpers
    private static void resetPlayer(Lane l) {
        FakePlayer p = l.player;
        p.moveTo(l.origin.x, l.origin.y, l.origin.z, 180, 0);
        p.setYHeadRot(180);
        p.setDeltaMovement(Vec3.ZERO);
        p.removeAllEffects();
        p.clearFire();
        p.setHealth(p.getMaxHealth());
        p.getFoodData().setFoodLevel(20);
        p.fallDistance = 0;
    }

    private static void refill(Lane l) {
        HybridData d = l.data();
        d.setBlood(HybridData.MAX_BLOOD);
        d.clearCooldowns();
        l.player.setHealth(l.player.getMaxHealth());
        l.player.getFoodData().setFoodLevel(20);
    }

    /** A tough dummy {@code dist} blocks in front of the lane's player (who faces north). */
    private static Husk target(Lane l, double dist) {
        ServerLevel level = l.level();
        for (Husk h : level.getEntitiesOfClass(Husk.class, area(l))) {
            h.discard();
        }
        Husk husk = EntityType.HUSK.create(level);
        if (husk == null) {
            throw new IllegalStateException("no husk");
        }
        husk.moveTo(l.origin.x, l.origin.y, l.origin.z - dist, 0, 0);
        husk.setNoAi(true);
        husk.setSilent(true);
        husk.setPersistenceRequired();
        husk.getAttribute(Attributes.MAX_HEALTH).setBaseValue(500);
        husk.setHealth(500);
        level.addFreshEntity(husk);
        return husk;
    }

    private static AABB area(Lane l) {
        return new AABB(l.origin, l.origin).inflate(11, 24, 18);
    }

    private static void clearArea(Lane l) {
        for (Entity e : l.level().getEntities((Entity) null, area(l), e -> !(e instanceof Player))) {
            if (e instanceof LivingEntity || e instanceof ItemEntity
                    || CsmMod.MODID.equals(EntityType.getKey(e.getType()).getNamespace())) {
                e.discard();
            }
        }
        l.player.removeAllEffects();
    }

    private SmokeTest() {
    }
}
