import AVFoundation
import AppKit
import Foundation

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let videoURL = root.appendingPathComponent("work/OfferGuard-competition-demo.mp4")
let asset = AVURLAsset(url: videoURL)
print("duration=\(CMTimeGetSeconds(asset.duration))")

for track in asset.tracks {
    print("track=\(track.mediaType.rawValue) nominal=\(track.nominalFrameRate) size=\(track.naturalSize)")
    for description in track.formatDescriptions {
        let format = description as! CMFormatDescription
        let codec = CMFormatDescriptionGetMediaSubType(format)
        let chars: [Character] = [
            Character(UnicodeScalar((codec >> 24) & 0xFF)!),
            Character(UnicodeScalar((codec >> 16) & 0xFF)!),
            Character(UnicodeScalar((codec >> 8) & 0xFF)!),
            Character(UnicodeScalar(codec & 0xFF)!),
        ]
        print("codec=\(String(chars))")
    }
}

let generator = AVAssetImageGenerator(asset: asset)
generator.appliesPreferredTrackTransform = true
generator.maximumSize = CGSize(width: 1920, height: 1080)
let outputDirectory = root.appendingPathComponent("tmp/video-frames")
try? FileManager.default.createDirectory(at: outputDirectory, withIntermediateDirectories: true)

for (index, second) in [1.0, 50.0, 120.0, 210.0, 275.0, 315.0].enumerated() {
    let image = try generator.copyCGImage(at: CMTime(seconds: second, preferredTimescale: 600), actualTime: nil)
    let representation = NSBitmapImageRep(cgImage: image)
    let data = representation.representation(using: .png, properties: [:])!
    let output = outputDirectory.appendingPathComponent("frame-\(index + 1)-\(Int(second)).png")
    try data.write(to: output)
    print("frame=\(output.path)")
}
