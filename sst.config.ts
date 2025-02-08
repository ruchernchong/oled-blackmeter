/// <reference path="./.sst/platform/config.d.ts" />
export default $config({
  app(input) {
    return {
      name: "oled-blackmeter",
      removal: input?.stage === "production" ? "retain" : "remove",
      protect: ["production"].includes(input?.stage),
      home: "aws",
      providers: {
        gcp: {
          version: "8.18.0",
          project: "oled-blackmeter",
        },
      },
    };
  },
  async run() {
    const bucket = new gcp.storage.Bucket("bucket", {
      location: "asia-southeast1",
    });

    const object = new gcp.storage.BucketObject("archive", {
      bucket: bucket.name,
      source: "",
    });

    const _function = new gcp.cloudfunctionsv2.Function("function", {
      location: "asia-southeast1",
      buildConfig: {
        runtime: "python312",
        entryPoint: "main",
        environmentVariables: {
          TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN,
        },
        source: {
          storageSource: {
            bucket: bucket.name,
            object: object.name,
          },
        },
      },
    });
  },
});
