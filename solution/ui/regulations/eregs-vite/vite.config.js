import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue2";
import { VuetifyResolver } from "unplugin-vue-components/resolvers";
import Components from "unplugin-vue-components/vite";

const path = require("path");

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        Components({
            resolvers: [VuetifyResolver()],
        }),
    ],
    css: {
        preprocessorOptions: {
            scss: {
                additionalData: `@import "../css/scss/main.scss";`,
            },
        },
    },
    resolve: {
        alias: {
            legacy: path.resolve(__dirname, "../../regulations"),
            eregsComponentLib: path.resolve(
                __dirname,
                "../../regulations/eregs-component-lib"
            ),
            "@": path.resolve(__dirname, "src"),
        },
    },
    build: {
        outDir: "../../../static-assets/regulations/vite",
        sourcemap: true,
        rollupOptions: {
            output: {
                entryFileNames: `[name].js`,
                chunkFileNames: `[name].js`,
                assetFileNames: `[name].[ext]`,
            },
        },
    },
});
