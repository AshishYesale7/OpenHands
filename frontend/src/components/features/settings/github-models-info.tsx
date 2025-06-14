import React from "react";
import { Card, CardBody, Chip } from "@heroui/react";

interface GitHubModelsInfoProps {
  selectedModel?: string;
}

export function GitHubModelsInfo({ selectedModel }: GitHubModelsInfoProps) {
  if (!selectedModel?.startsWith("github/")) {
    return null;
  }

  return (
    <div className="space-y-4">
      <Card className="bg-tertiary border border-[#717888]">
        <CardBody className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <h3 className="text-lg font-semibold">GitHub Models</h3>
            <Chip size="sm" color="primary" variant="flat">
              Auto-Fallback
            </Chip>
          </div>

          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-300">
                GitHub Models provides access to multiple AI models with
                automatic fallback when rate limits are reached.
              </p>
            </div>

            <div>
              <h4 className="font-medium text-sm mb-2">Features</h4>
              <ul className="text-sm text-gray-300 space-y-1">
                <li>• Automatic model switching on rate limits</li>
                <li>• Access to 59+ models from multiple providers</li>
                <li>• Single GitHub API key for all models</li>
                <li>• Intelligent tier-based fallback system</li>
              </ul>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
