import AVFoundation
import AppKit
import CoreGraphics
import CoreText
import CoreVideo
import Foundation

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let outputURL = root.appendingPathComponent("work/offerguard-demo-video.mp4")
let assets = root.appendingPathComponent("assets")
let width = 1920
let height = 1080
let fps: Int32 = 12
let totalDuration: Double = 330
let frameCount = Int(totalDuration * Double(fps))
let transitionDuration: Double = 0.8

let sceneFiles = [
    "landing-screen.png",
    "workspace-screen.png",
    "report-screen.png",
    "action-screen.png",
    "risk-screen.png",
    "landing-screen.png",
]
let sceneStarts: [Double] = [0, 38, 92, 184, 252, 305]
let sceneTitles = [
    ("AI-NATIVE 就业风险侦察", "签字之前，先看见代价。"),
    ("01 / RISK SCAN", "输入合同，观察六阶段 Agent 轨迹。"),
    ("02 / EVIDENCE CHAIN", "每一个风险，都回到原文与可信证据。"),
    ("03 / ACTION PLAN", "核对原文后，人工确认才解锁草稿。"),
    ("04 / HOW IT THINKS", "让 AI 负责发现，让你保留决定权。"),
    ("OFFERGUARD · 职途罗盘", "看见每一份 offer 的隐藏代价。"),
]

let images: [NSImage] = sceneFiles.map { filename in
    let path = assets.appendingPathComponent(filename).path
    guard let image = NSImage(contentsOfFile: path) else {
        fatalError("Missing screenshot: \(path)")
    }
    return image
}

func removeIfNeeded(_ url: URL) {
    if FileManager.default.fileExists(atPath: url.path) {
        try? FileManager.default.removeItem(at: url)
    }
}

func drawText(
    _ text: String,
    x: CGFloat,
    y: CGFloat,
    size: CGFloat,
    color: NSColor,
    weight: NSFont.Weight = .regular,
    maxWidth: CGFloat? = nil
) {
    let font = NSFont.systemFont(ofSize: size, weight: weight)
    let paragraph = NSMutableParagraphStyle()
    paragraph.lineBreakMode = .byTruncatingTail
    let attributes: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: color,
        .paragraphStyle: paragraph,
    ]
    let attributed = NSAttributedString(string: text, attributes: attributes)
    let bounds = maxWidth.map { NSSize(width: $0, height: size * 2) } ?? NSSize(width: 1800, height: size * 2)
    attributed.draw(with: NSRect(x: x, y: y, width: bounds.width, height: bounds.height), options: [.usesLineFragmentOrigin])
}

func drawImage(_ image: NSImage, alpha: CGFloat, progress: Double, context: CGContext) {
    let zoom = 1.035 + CGFloat(progress) * 0.025
    let drawWidth = CGFloat(width) * zoom
    let drawHeight = CGFloat(height) * zoom
    let drawX = (CGFloat(width) - drawWidth) / 2
    let drawY = (CGFloat(height) - drawHeight) / 2
    context.saveGState()
    context.setAlpha(alpha)
    image.draw(
        in: NSRect(x: drawX, y: drawY, width: drawWidth, height: drawHeight),
        from: .zero,
        operation: .sourceOver,
        fraction: alpha,
        respectFlipped: true,
        hints: [.interpolation: NSImageInterpolation.high]
    )
    context.restoreGState()
}

func sceneIndex(at second: Double) -> Int {
    var index = 0
    for (candidate, start) in sceneStarts.enumerated() where second >= start {
        index = candidate
    }
    return index
}

func renderFrame(second: Double, context: CGContext) {
    let current = sceneIndex(at: second)
    let currentStart = sceneStarts[current]
    let currentEnd = current + 1 < sceneStarts.count ? sceneStarts[current + 1] : totalDuration
    let progress = min(1, max(0, (second - currentStart) / (currentEnd - currentStart)))

    context.setFillColor(NSColor(calibratedRed: 0.956, green: 0.937, blue: 0.894, alpha: 1).cgColor)
    context.fill(CGRect(x: 0, y: 0, width: width, height: height))
    drawImage(images[current], alpha: 1, progress: progress, context: context)

    if current + 1 < images.count {
        let untilEnd = currentEnd - second
        if untilEnd < transitionDuration {
            let alpha = CGFloat(1 - untilEnd / transitionDuration)
            drawImage(images[current + 1], alpha: alpha, progress: 0, context: context)
        }
    }

    let shade = CGGradient(
        colorsSpace: CGColorSpaceCreateDeviceRGB(),
        colors: [
            NSColor(calibratedWhite: 0.03, alpha: 0).cgColor,
            NSColor(calibratedWhite: 0.03, alpha: 0.12).cgColor,
            NSColor(calibratedWhite: 0.03, alpha: 0.88).cgColor,
        ] as CFArray,
        locations: [0, 0.7, 1]
    )!
    context.drawLinearGradient(
        shade,
        start: CGPoint(x: 0, y: 720),
        end: CGPoint(x: 0, y: 1080),
        options: []
    )

    let sceneAlpha = current == 5 ? min(1, CGFloat((second - 305) / 1.2)) : 1
    context.saveGState()
    context.setAlpha(sceneAlpha)
    let title = sceneTitles[current]
    drawText(
        title.0.uppercased(),
        x: 76,
        y: 858,
        size: 20,
        color: NSColor(calibratedRed: 0.84, green: 0.93, blue: 0.51, alpha: 1),
        weight: .medium
    )
    drawText(
        title.1,
        x: 72,
        y: 894,
        size: 46,
        color: .white,
        weight: .semibold,
        maxWidth: 1500
    )
    drawText(
        "OFFERGUARD / TECHNICAL DEMO / 2026",
        x: 1370,
        y: 1020,
        size: 15,
        color: NSColor(calibratedWhite: 1, alpha: 0.48),
        weight: .medium
    )
    context.restoreGState()

    context.setFillColor(NSColor(calibratedWhite: 1, alpha: 0.14).cgColor)
    context.fill(CGRect(x: 0, y: 1074, width: CGFloat(width), height: 5))
    context.setFillColor(NSColor(calibratedRed: 0.84, green: 0.93, blue: 0.51, alpha: 1).cgColor)
    context.fill(CGRect(x: 0, y: 1074, width: CGFloat(width) * CGFloat(second / totalDuration), height: 5))
}

removeIfNeeded(outputURL)
try? FileManager.default.createDirectory(
    at: outputURL.deletingLastPathComponent(),
    withIntermediateDirectories: true
)

let writer = try AVAssetWriter(outputURL: outputURL, fileType: .mp4)
let videoSettings: [String: Any] = [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width,
    AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [
        AVVideoAverageBitRateKey: 7_500_000,
        AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel,
        AVVideoMaxKeyFrameIntervalKey: 24,
    ],
]
let input = AVAssetWriterInput(mediaType: .video, outputSettings: videoSettings)
input.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(
    assetWriterInput: input,
    sourcePixelBufferAttributes: [
        kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
        kCVPixelBufferWidthKey as String: width,
        kCVPixelBufferHeightKey as String: height,
        kCVPixelBufferCGImageCompatibilityKey as String: true,
        kCVPixelBufferCGBitmapContextCompatibilityKey as String: true,
    ]
)
guard writer.canAdd(input) else {
    fatalError("Cannot add video input")
}
writer.add(input)
writer.startWriting()
writer.startSession(atSourceTime: .zero)

let queue = DispatchQueue(label: "offerguard.render")
let semaphore = DispatchSemaphore(value: 0)
input.requestMediaDataWhenReady(on: queue) {
    for frame in 0..<frameCount {
        while !input.isReadyForMoreMediaData {
            Thread.sleep(forTimeInterval: 0.002)
        }
        var optionalBuffer: CVPixelBuffer?
        CVPixelBufferCreate(
            kCFAllocatorDefault,
            width,
            height,
            kCVPixelFormatType_32BGRA,
            [
                kCVPixelBufferCGImageCompatibilityKey: true,
                kCVPixelBufferCGBitmapContextCompatibilityKey: true,
            ] as CFDictionary,
            &optionalBuffer
        )
        guard let buffer = optionalBuffer else {
            fatalError("Unable to create pixel buffer")
        }
        CVPixelBufferLockBaseAddress(buffer, [])
        let context = CGContext(
            data: CVPixelBufferGetBaseAddress(buffer),
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: CVPixelBufferGetBytesPerRow(buffer),
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.premultipliedFirst.rawValue |
                CGBitmapInfo.byteOrder32Little.rawValue
        )!
        context.translateBy(x: 0, y: CGFloat(height))
        context.scaleBy(x: 1, y: -1)
        NSGraphicsContext.saveGraphicsState()
        NSGraphicsContext.current = NSGraphicsContext(cgContext: context, flipped: true)
        renderFrame(second: Double(frame) / Double(fps), context: context)
        NSGraphicsContext.restoreGraphicsState()
        CVPixelBufferUnlockBaseAddress(buffer, [])
        let presentationTime = CMTime(value: Int64(frame), timescale: fps)
        if !adaptor.append(buffer, withPresentationTime: presentationTime) {
            fatalError("Failed to append frame \(frame)")
        }
        if frame % 240 == 0 {
            print("Rendered \(frame)/\(frameCount) frames")
        }
    }
    input.markAsFinished()
    writer.finishWriting {
        semaphore.signal()
    }
}

semaphore.wait()
if writer.status != .completed {
    fatalError("Video render failed: \(String(describing: writer.error))")
}
print("Rendered video: \(outputURL.path) / \(totalDuration) seconds")
