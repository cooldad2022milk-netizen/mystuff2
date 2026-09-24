package com.csm.hybrids.client.dev;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.client.screen.AbilityWheelScreen;
import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridLogic;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModItems;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.Difficulty;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.WorldDataConfiguration;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

/**
 * Screenshot showcase, only active with {@code -Dcsm.showcase=true} (see README: {@code gradlew runClient -PcsmShowcase}).
 * Creates a flat creative world, performs every heart replacement, trigger and ability for each hybrid and saves
 * screenshots named csm_*.png into run/screenshots, then quits.
 */
@Mod.EventBusSubscriber(modid = CsmMod.MODID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
public final class DevShowcase {
    private static final boolean ENABLED = Boolean.getBoolean("csm.showcase");
    private static boolean started;
    private static int tick = -1;
    private static final List<Step> STEPS = new ArrayList<>();

    private record Step(int at, Runnable action) {
    }

    @SubscribeEvent
    public static void onScreen(ScreenEvent.Init.Post event) {
        if (!ENABLED || started || !(event.getScreen() instanceof TitleScreen)) {
            return;
        }
        started = true;
        buildScript();
        Minecraft mc = Minecraft.getInstance();
        mc.options.pauseOnLostFocus = false; // the tour must keep running if the window loses focus
        String name = "csm_showcase_" + System.currentTimeMillis();
        GameRules rules = new GameRules();
        rules.getRule(GameRules.RULE_DAYLIGHT).set(false, null);
        rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false, null);
        rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false, null);
        LevelSettings settings = new LevelSettings(name, GameType.CREATIVE, false, Difficulty.NORMAL, true, rules,
                WorldDataConfiguration.DEFAULT);
        WorldOptions options = new WorldOptions(20240101L, false, false);
        mc.createWorldOpenFlows().createFreshLevel(name, settings, options,
                access -> access.registryOrThrow(Registries.WORLD_PRESET).getHolderOrThrow(WorldPresets.FLAT).value()
                        .createWorldDimensions());
    }

    @SubscribeEvent
    public static void onTick(TickEvent.ClientTickEvent event) {
        if (!ENABLED || event.phase != TickEvent.Phase.END) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.getSingleplayerServer() == null || mc.level == null) {
            return;
        }
        if (mc.screen instanceof net.minecraft.client.gui.screens.PauseScreen) {
            mc.setScreen(null);
        }
        tick++;
        for (Step s : STEPS) {
            if (s.at == tick) {
                try {
                    s.action.run();
                } catch (Exception e) {
                    CsmMod.LOGGER.error("[showcase] step at {} failed", tick, e);
                }
            }
        }
    }

    // ------------------------------------------------------------------ script
    private static int t;

    private static void at(int dt, Runnable r) {
        t += dt;
        STEPS.add(new Step(t, r));
    }

    private static void buildScript() {
        t = 40;
        at(0, () -> {
            cmd("time set noon");
            cmd("weather clear");
            cmd("gamerule mobGriefing false");
            cmd("tp @s 0 -60 0 180 5");
            Minecraft.getInstance().options.setCameraType(CameraType.THIRD_PERSON_FRONT);
            Minecraft.getInstance().options.hideGui = false;
            Minecraft.getInstance().getTutorial().setStep(net.minecraft.client.tutorial.TutorialSteps.NONE);
        });
        String filter = System.getProperty("csm.showcase.types", "").trim();
        String devils = System.getProperty("csm.showcase.devils", "").trim();
        List<String> full = filter.isEmpty() ? List.of("chainsaw", "crossbow", "flamethrower", "whip", "bomb", "spear")
                : List.of(filter.split(","));
        if (devils.isEmpty() || !filter.isEmpty()) {
            for (HybridType type : HybridType.values()) {
                if (type == HybridType.NONE || type.devil) {
                    continue;
                }
                if (full.contains(type.id)) {
                    fullTour(type);
                } else if (devils.isEmpty()) {
                    firstPersonPass(type);
                }
            }
        }
        for (String id : devils.isEmpty() ? new String[0] : devils.split(",")) {
            devilTour(HybridType.byId(id));
        }
        at(20, () -> Minecraft.getInstance().stop());
    }

    /** A tough, brain-dead husk 6 blocks in front of the player (behind the front camera) to aim moves at. */
    private static void target() {
        cmd("kill @e[type=minecraft:husk]");
        cmd("summon minecraft:husk 0 -60 -6 {NoAI:1b,Silent:1b,PersistenceRequired:1b,DeathLootTable:\"minecraft:empty\",Health:500f,"
                + "Attributes:[{Name:\"generic.max_health\",Base:500d}]}");
    }

    private static void becomeHybrid(HybridType type, boolean shots) {
        String id = type.id;
        // loot from earlier targets (rotten flesh) must not end up in the hand holding the heart
        at(6, () -> {
            cmd("kill @e[type=minecraft:item]");
            cmd("clear @s");
        });
        at(4, () -> server(p -> {
            p.teleportTo(0, -60, 0);
            p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(ModItems.heartFor(type)));
            p.getItemInHand(InteractionHand.MAIN_HAND).use(p.level(), p, InteractionHand.MAIN_HAND);
            p.setYRot(180);
            p.setYHeadRot(180);
        }));
        if (shots) {
            at(22, () -> shot(id + "_00_heart_rip"));
            at(40, () -> fillBlood(true));
            at(8, () -> shot(id + "_01_human"));
        } else {
            at(62, () -> fillBlood(true));
        }
    }

    private static void fillBlood(boolean emptyHand) {
        server(p -> {
            HybridData d = HybridCapability.get(p);
            if (emptyHand && d != null) {
                CsmMod.LOGGER.info("[showcase] player is now: {}", d.type().id);
            }
            if (d != null) {
                d.setBlood(100);
                HybridLogic.sync(p, d);
            }
            if (emptyHand) {
                p.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
            }
        });
    }

    /** Where the player ended up and how hurt the target is (moves that teleport / pull are hard to judge from a shot). */
    private static void logState(String tag) {
        server(p -> {
            List<net.minecraft.world.entity.monster.Husk> husks = p.level().getEntitiesOfClass(
                    net.minecraft.world.entity.monster.Husk.class, p.getBoundingBox().inflate(40), h -> h.isAlive());
            String husk = husks.isEmpty() ? "none" : String.format("%.0f hp at %.1f %.1f %.1f", husks.get(0).getHealth(),
                    husks.get(0).getX(), husks.get(0).getY(), husks.get(0).getZ());
            CsmMod.LOGGER.info("[showcase] {}: player at {} {} {} yaw {}, husk {}", tag, String.format("%.1f", p.getX()),
                    String.format("%.1f", p.getY()), String.format("%.1f", p.getZ()), (int) p.getYRot(), husk);
        });
    }

    private static int[] triggerFrames(HybridType type) {
        return switch (type) {
            case CHAINSAW -> new int[]{3, 6, 10, 13, 20};
            case CROSSBOW -> new int[]{5, 9, 14, 18, 23};
            case WHIP -> new int[]{3, 6, 8, 10, 14};
            case BOMB -> new int[]{5, 8, 10, 13, 18};
            case SPEAR -> new int[]{5, 8, 12, 16, 20};
            case KATANA, LONGSWORD -> new int[]{4, 7, 10, 13, 18};
            case BLOOD -> new int[]{4, 7, 10, 12, 16};
            case SHARK -> new int[]{3, 6, 9, 11, 15};
            case VIOLENCE -> new int[]{5, 8, 11, 14, 18};
            case COSMOS, GUN -> new int[]{4, 8, 11, 14, 18};
            default -> new int[]{5, 8, 10, 14, 20};
        };
    }

    private static void fullTour(HybridType type) {
        String id = type.id;
        becomeHybrid(type, true);
        // trigger
        int[] frames = triggerFrames(type);
        // the spear is drawn out of the back of the neck: film that one from behind
        boolean fromBehind = type == HybridType.SPEAR;
        if (fromBehind) {
            at(2, () -> Minecraft.getInstance().options.setCameraType(CameraType.THIRD_PERSON_BACK));
        }
        at(4, () -> server(p -> HybridLogic.tryUseAbility(p, 0)));
        int prev = 0;
        for (int i = 0; i < frames.length; i++) {
            int f = frames[i];
            int idx = i;
            at(f - prev, () -> shot(id + "_02_trigger_" + idx));
            prev = f;
        }
        if (fromBehind) {
            at(2, () -> Minecraft.getInstance().options.setCameraType(CameraType.THIRD_PERSON_FRONT));
        }
        at(30, () -> shot(id + "_03_form"));
        at(2, () -> Minecraft.getInstance().options.setCameraType(CameraType.THIRD_PERSON_BACK));
        at(3, () -> shot(id + "_04_form_back"));
        at(2, () -> Minecraft.getInstance().options.setCameraType(CameraType.THIRD_PERSON_FRONT));
        // every ability (skip slot 0 = trigger), each with two frames
        int count = type.abilities().size();
        for (int i = 1; i < count; i++) {
            int slot = i;
            int wait = type.abilities().get(i).duration();
            int a = Math.max(3, Math.min(wait / 3, 8));
            int b = Math.max(3, Math.min(wait / 3, 8));
            at(4, () -> {
                target();
                fillBlood(false);
            });
            at(4, () -> server(p -> HybridLogic.tryUseAbility(p, slot)));
            at(a, () -> shot(id + "_05_ability_" + slot + "a"));
            at(b, () -> {
                shot(id + "_05_ability_" + slot + "b");
                logState(id + " ability " + slot);
            });
            at(Math.max(wait - a - b, 2) + 8, () -> server(p -> {
                p.teleportTo(0, -60, 0);
                p.setYRot(180);
                p.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);
            }));
        }
        at(4, () -> cmd("kill @e[type=minecraft:husk]"));
        // ability wheel
        at(6, () -> Minecraft.getInstance().setScreen(new AbilityWheelScreen(type, false)));
        at(8, () -> shot(id + "_06_wheel"));
        at(2, () -> Minecraft.getInstance().setScreen(null));
        firstPersonMoves(type, 1, 2);
        // put it away
        at(4, () -> server(p -> HybridLogic.tryUseAbility(p, 0)));
        at(16, () -> shot(id + "_08_reverted"));
    }

    /** Only checks the devil arms in first person while moves play (the bug where they vanished). */
    private static void firstPersonPass(HybridType type) {
        becomeHybrid(type, false);
        at(4, () -> server(p -> HybridLogic.tryUseAbility(p, 0)));
        at(type.triggerTicks + 20, () -> {
        });
        firstPersonMoves(type, 1, 2);
        at(4, () -> server(p -> HybridLogic.tryUseAbility(p, 0)));
        at(type.revertTicks + 8, () -> {
        });
    }

    private static void firstPersonMoves(HybridType type, int... slots) {
        String id = type.id;
        at(4, () -> Minecraft.getInstance().options.setCameraType(CameraType.FIRST_PERSON));
        at(6, () -> shot(id + "_07_first_person"));
        for (int slot : slots) {
            int wait = type.abilities().get(slot).duration();
            at(2, () -> {
                fillBlood(false);
                server(p -> {
                    p.teleportTo(0, -60, 0);
                    p.setYRot(180);
                    p.setXRot(10);
                });
            });
            at(4, () -> server(p -> HybridLogic.tryUseAbility(p, slot)));
            int a = Math.max(2, Math.min(wait / 3, 6));
            at(a, () -> shot(id + "_07_first_person_move" + slot + "a"));
            at(Math.max(2, wait / 3), () -> shot(id + "_07_first_person_move" + slot + "b"));
            at(Math.max(wait - a - wait / 3, 2) + 6, () -> {
            });
        }
        at(2, () -> Minecraft.getInstance().options.setCameraType(CameraType.THIRD_PERSON_FRONT));
    }

    // ------------------------------------------------------------------ full devils
    private static com.csm.hybrids.entity.devil.DevilEntity devil;

    /** The devil as a mob (every move forced once against a dummy), then the player becoming it. */
    private static void devilTour(HybridType type) {
        String id = "devil_" + type.id;
        at(6, () -> {
            cmd("kill @e[type=!minecraft:player]");
            cmd("clear @s");
            server(p -> {
                p.teleportTo(0, -60, 8);
                p.setYRot(180);
                p.setYHeadRot(180);
                p.setXRot(8);
            });
            Minecraft.getInstance().options.setCameraType(CameraType.FIRST_PERSON);
        });
        at(4, () -> server(p -> {
            cmd("summon minecraft:husk 3 -60 -6 {NoAI:1b,Silent:1b,PersistenceRequired:1b,DeathLootTable:\"minecraft:empty\","
                    + "Health:500f,Attributes:[{Name:\"generic.max_health\",Base:500d}]}");
            devil = com.csm.hybrids.registry.ModEntities.devil(type).create(p.level());
            if (devil != null) {
                devil.moveTo(-3, type == HybridType.BAT || type == HybridType.ANGEL ? -58 : -60, -8, 0, 0);
                devil.setPersistenceRequired();
                p.level().addFreshEntity(devil);
            }
        }));
        at(20, () -> shot(id + "_00_mob"));
        List<com.csm.hybrids.ability.devil.DevilAbility> moves = new ArrayList<>();
        for (com.csm.hybrids.ability.Ability a : type.abilities()) {
            if (a instanceof com.csm.hybrids.ability.devil.DevilAbility d && d.mobUse) {
                moves.add(d);
            }
        }
        for (int i = 0; i < moves.size(); i++) {
            int idx = i;
            com.csm.hybrids.ability.devil.DevilAbility m = moves.get(i);
            at(10, () -> server(p -> {
                net.minecraft.world.entity.monster.Husk husk = p.level().getEntitiesOfClass(
                        net.minecraft.world.entity.monster.Husk.class, p.getBoundingBox().inflate(40), h -> h.isNoAi())
                        .stream().findFirst().orElse(null);
                if (devil != null && husk != null && devil.isAlive()) {
                    // stand at the distance the move is meant for
                    double d = Math.max(0.5, Math.min((m.aiMin + m.aiMax) / 2, 8)) + (devil.getBbWidth() + husk.getBbWidth()) / 2;
                    devil.moveTo(husk.getX() - d, devil.getY(), husk.getZ(), -90, 0);
                    devil.face(husk);
                    devil.setTarget(husk);
                    devil.startMove(m, idx, husk);
                }
            }));
            int a = Math.max(3, Math.min(m.duration() / 2, 12));
            at(a, () -> shot(id + "_01_mob_move" + idx + "a"));
            at(Math.max(3, m.duration() - a), () -> {
                shot(id + "_01_mob_move" + idx + "b");
                logState(id + " mob move " + idx);
            });
        }
        at(6, () -> server(p -> {
            if (devil != null) {
                devil.kill(); // (a normal blow can't kill Makima while anything else is alive nearby)
            }
        }));
        at(8, () -> shot(id + "_02_mob_death"));
        // the player swallows its essence
        at(30, () -> {
            cmd("kill @e[type=minecraft:item]");
            Minecraft.getInstance().options.setCameraType(CameraType.THIRD_PERSON_FRONT);
            server(p -> {
                p.teleportTo(0, -60, 0);
                p.setYRot(180);
                p.setYHeadRot(180);
                p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(ModItems.heartFor(type)));
                p.getItemInHand(InteractionHand.MAIN_HAND).use(p.level(), p, InteractionHand.MAIN_HAND);
            });
        });
        at(22, () -> shot(id + "_03_swallow"));
        at(40, () -> fillBlood(true));
        at(6, () -> shot(id + "_04_human"));
        at(4, () -> server(p -> HybridLogic.tryUseAbility(p, 0)));
        int prev = 0;
        for (int f : new int[]{6, 11, 14, 20}) {
            int fr = f;
            at(f - prev, () -> shot(id + "_05_manifest_" + fr));
            prev = f;
        }
        at(20, () -> shot(id + "_06_form"));
        at(2, () -> Minecraft.getInstance().options.setCameraType(CameraType.THIRD_PERSON_BACK));
        at(3, () -> shot(id + "_07_form_back"));
        at(2, () -> Minecraft.getInstance().options.setCameraType(CameraType.THIRD_PERSON_FRONT));
        int count = type.abilities().size();
        for (int i = 1; i < count - 1; i++) {
            int slot = i;
            int wait = type.abilities().get(i).duration();
            double reach = type.abilities().get(i) instanceof com.csm.hybrids.ability.devil.DevilAbility da
                    ? Math.max(0.5, Math.min((da.aiMin + da.aiMax) / 2, 8)) : 5;
            at(4, () -> {
                server(p -> {
                    double d = reach + p.getBbWidth() / 2 + 0.3;
                    cmd("kill @e[type=minecraft:husk]");
                    cmd(String.format(java.util.Locale.ROOT, "summon minecraft:husk 0.5 -60 %.2f {NoAI:1b,Silent:1b,"
                            + "PersistenceRequired:1b,DeathLootTable:\"minecraft:empty\",Health:500f,Attributes:[{Name:"
                            + "\"generic.max_health\",Base:500d}]}", 0.5 - d));
                });
                fillBlood(false);
            });
            at(4, () -> server(p -> HybridLogic.tryUseAbility(p, slot)));
            int a = Math.max(3, Math.min(wait / 2, 10));
            at(a, () -> shot(id + "_08_ability_" + slot + "a"));
            at(Math.max(3, wait - a), () -> {
                shot(id + "_08_ability_" + slot + "b");
                logState(id + " ability " + slot);
            });
            at(10, () -> server(p -> {
                p.teleportTo(0, -60, 0);
                p.setYRot(180);
                p.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);
            }));
        }
        firstPersonMoves(type, 1, 2);
        at(4, () -> server(p -> HybridLogic.tryUseAbility(p, 0)));
        at(24, () -> shot(id + "_09_reverted"));
    }

    private static void cmd(String command) {
        MinecraftServer server = Minecraft.getInstance().getSingleplayerServer();
        if (server != null) {
            server.execute(() -> {
                ServerPlayer p = server.getPlayerList().getPlayers().get(0);
                server.getCommands().performPrefixedCommand(p.createCommandSourceStack().withPermission(4), command);
            });
        }
    }

    private static void server(Consumer<ServerPlayer> action) {
        MinecraftServer server = Minecraft.getInstance().getSingleplayerServer();
        if (server != null) {
            server.execute(() -> action.accept(server.getPlayerList().getPlayers().get(0)));
        }
    }

    private static void shot(String name) {
        Minecraft mc = Minecraft.getInstance();
        mc.gui.getChat().clearMessages(false);
        Screenshot.grab(mc.gameDirectory, "csm_" + name + ".png", mc.getMainRenderTarget(), msg -> {
        });
        CsmMod.LOGGER.info("[showcase] screenshot {}", name);
    }

    private DevShowcase() {
    }
}
